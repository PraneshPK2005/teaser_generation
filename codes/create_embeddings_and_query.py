from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os
import re

# -----------------------------
# Load embedding model
# -----------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# -----------------------------
# Function to create FAISS index
# -----------------------------
def create_index(data, index_path, mapping_path):
    """
    data: list of dicts with keys 'timestamp' and 'text'
    index_path: path to save the FAISS index
    mapping_path: path to save the mapping JSON
    """
    texts = [d["text"] for d in data]
    embeddings = model.encode(texts, convert_to_numpy=True).astype('float32')

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    faiss.write_index(index, index_path)
    
    # Save mapping
    with open(mapping_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Index saved at {index_path}")
    print(f"Mapping saved at {mapping_path}")
    return index

# -----------------------------
# Load indexes and mappings
# -----------------------------
def load_index(index_path, mapping_path):
    index = faiss.read_index(index_path)
    with open(mapping_path) as f:
        mapping = json.load(f)
    return index, mapping

# -----------------------------
# Query function
# -----------------------------
def query_index(index, mapping, query, top_k):
    embedding = model.encode([query], convert_to_numpy=True).astype('float32')
    distances, indices = index.search(embedding, top_k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            "timestamp": mapping[idx]["timestamp"],
            "text": mapping[idx]["text"],
            "score": float(dist)
        })
    return results

# -------------------------------
# New function to format results for Ollama
# -------------------------------
def format_for_ollama(results):
    """
    Sort the results by score descending and return only timestamp and text.
    Args:
        results (list of dicts): [{'timestamp':..., 'text':..., 'score':...}, ...]
    Returns:
        formatted (list of dicts): [{'timestamp':..., 'text':...}, ...] sorted by score desc
    """
    # Sort descending by score
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    # Keep only timestamp and text
    formatted = [{'timestamp': item['timestamp'], 'text': item['text']} for item in sorted_results]
    
    return formatted

# -------------------------------
# Function to parse timestamps
# -------------------------------
def parse_audio_timestamp(ts: str):
    """
    Example input: '[0.00s - 4.23s]'
    Returns duration in seconds as float
    """
    match = re.match(r"\[(\d+\.?\d*)s\s*-\s*(\d+\.?\d*)s\]", ts)
    if match:
        start, end = float(match.group(1)), float(match.group(2))
        return end - start
    return 0.0

def parse_visual_timestamp(ts: str):
    """
    Example input: '[0.00s]'
    Returns duration in seconds (assume 1.5s per visual)
    """
    match = re.match(r"\[(\d+\.?\d*)s\]", ts)
    if match:
        return float(match.group(1)), float(match.group(1)) + 1.5
    return 0.0, 0.0

# -------------------------------
# Function to estimate top_k dynamically
# -------------------------------
def estimate_top_k(method, audio_data, visual_data=None, max_length=None, min_length=None):
    """
    Returns top_audio, top_visual based on method and average durations
    """
    # Compute average audio duration
    audio_durations = [parse_audio_timestamp(d['timestamp']) for d in audio_data]
    avg_audio = sum(audio_durations) / len(audio_durations) if audio_durations else 1.0

    if method == "learning_a":
        top_audio = int(( (min_length + max_length)/2 / avg_audio ) + 3)
        top_visual = 0

    else:
        # Compute average visual duration
        visual_durations = []
        for d in visual_data:
            start, end = parse_visual_timestamp(d['timestamp'])
            visual_durations.append(end - start)
        avg_visual = sum(visual_durations) / len(visual_durations) if visual_durations else 1.0

        if method == "learning_b":
            top_audio = int(( (min_length + max_length)/2 / avg_audio ) + 3)
            top_visual = int(( (min_length + max_length)/2 / avg_visual ) + 3)

        elif method == "cinematic_a":
            top_visual = int(( ((min_length + max_length)/2)*0.8 / avg_visual ) + 3)
            top_audio = int(( ((min_length + max_length)/2)*0.2 / avg_audio ) + 3)
        else:
            raise ValueError("Invalid method")

    return top_audio, top_visual

# -----------------------------
# Dynamic Teaser Embedding Pipeline
# -----------------------------
def teaser_pipeline(method, max_length, min_length,audio_data=None, visual_data=None, query_audio_text="best sentence for teaser", query_visual_text="best visuals for teaser"):
    """
    method: str, one of 'learning_a', 'learning_b', 'cinematic_a'
    audio_data, visual_data: list of dicts with keys 'timestamp' and 'text'
    Returns: formatted_audio, formatted_visual, total_duration
    """
    audio_index, visual_index = None, None
    audio_mapping, visual_mapping = None, None
    total_duration = 0

    # Determine indexing and top_k based on method
    if method == "learning_a":
        # Only audio
        create_index(audio_data, "audio_index.faiss", "audio_mapping.json")
        audio_index, audio_mapping = load_index("audio_index.faiss", "audio_mapping.json")
        top_audio, top_visual = estimate_top_k(method,max_length,min_length, audio_data)
        
        # Calculate total duration for audio method
        audio_durations = [parse_audio_timestamp(d['timestamp']) for d in audio_data]
        total_duration = sum(audio_durations) / len(audio_durations) * top_audio if audio_durations else 0

    elif method == "learning_b":
        # Both audio and visual
        create_index(audio_data, "audio_index.faiss", "audio_mapping.json")
        create_index(visual_data, "visual_index.faiss", "visual_mapping.json")
        audio_index, audio_mapping = load_index("audio_index.faiss", "audio_mapping.json")
        visual_index, visual_mapping = load_index("visual_index.faiss", "visual_mapping.json")
        top_audio, top_visual = estimate_top_k(method,max_length,min_length, audio_data, visual_data)
        
        # Calculate total duration for learning_b (based on visual segments)
        total_duration = top_visual * 1.5  # Each visual segment is 1.5 seconds

    elif method == "cinematic_a":
        # Both audio and visual
        create_index(audio_data, "audio_index.faiss", "audio_mapping.json")
        create_index(visual_data, "visual_index.faiss", "visual_mapping.json")
        audio_index, audio_mapping = load_index("audio_index.faiss", "audio_mapping.json")
        visual_index, visual_mapping = load_index("visual_index.faiss", "visual_mapping.json")
        top_audio, top_visual = estimate_top_k(method,max_length,min_length, audio_data, visual_data)
        
        # Calculate total duration for cinematic_a (based on visual segments)
        total_duration = top_visual * 1.5  # Each visual segment is 1.5 seconds

    else:
        raise ValueError("Invalid method")

    # Query indexes dynamically
    results_audio = query_index(audio_index, audio_mapping, query_audio_text, top_audio) if audio_index else []
    results_visual = query_index(visual_index, visual_mapping, query_visual_text, top_visual) if visual_index else []

    formatted_audio = format_for_ollama(results_audio)
    formatted_visual = format_for_ollama(results_visual)

    return formatted_audio, formatted_visual, total_duration

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Replace with your actual data
    audio_data=[{'timestamp': '[0.00s - 4.23s]', 'text': "Not only am I going to review an older movie for you guys, but I'm going to review one"}, {'timestamp': '[4.23s - 6.22s]', 'text': 'of my favorite movies, as in , ever.'}, {'timestamp': '[11.52s - 13.16s]', 'text': 'Terminator 2, Judgment Day.'}, {'timestamp': '[13.24s - 15.90s]', 'text': "I know what some of you are thinking right now, you're , wait, Terminator 2, where's"}, {'timestamp': '[15.90s - 16.58s]', 'text': 'Terminator 1?'}, {'timestamp': '[16.72s - 19.60s]', 'text': 'I wanted to go straight for the throat on this one, I wanted to review one of my favorite'}, {'timestamp': '[19.68s - 20.40s]', 'text': 'movies of all time.'}, {'timestamp': '[20.46s - 22.32s]', 'text': "But I'm not going to leave you hanging, here's a bit of the backstory."}, {'timestamp': '[22.40s - 27.47s]', 'text': 'In Terminator Lore, on August 29th, 1997, the machines we created became self-aware and'}, {'timestamp': '[27.47s - 28.66s]', 'text': 'they pretty much wiped out mankind.'}, {'timestamp': '[28.94s - 31.02s]', 'text': ", yeah, that didn't quite happen, but ."}, {'timestamp': '[31.20s - 35.00s]', 'text': "From that point of the year, 2029, mankind's been locked in a war with the machines."}, {'timestamp': '[35.18s - 38.60s]', 'text': 'The leader of this resistance is a man named John Conner and he leads mankind'}, {'timestamp': '[38.66s - 39.16s]', 'text': 'to victory.'}, {'timestamp': '[39.34s - 42.72s]', 'text': 'So in Terminator 1, the machines send a machine back in time to kill Sarah Connor.'}, {'timestamp': '[42.82s - 45.58s]', 'text': 'Yeah, no Sarah Connor means no John Connor means the machines win.'}, {'timestamp': '[45.76s - 47.34s]', 'text': 'And now we reach Terminator 2.'}, {'timestamp': '[47.50s - 51.14s]', 'text': 'Machines kinda had to failsafe, they sent two Terminators back through time, one'}, {'timestamp': '[51.18s - 55.04s]', 'text': 'back to the 80s to take out Sarah Connor, the other to the 90s to take out John Connor.'}, {'timestamp': '[55.14s - 57.40s]', 'text': "But don't worry, we humans were smart and we have a plan."}, {'timestamp': '[57.82s - 62.04s]', 'text': 'John Connor from the future reprograms the Terminator to protect him as a child in the 90s.'}, {'timestamp': '[62.18s - 64.20s]', 'text': "Now we have our movie and it's awesome."}, {'timestamp': '[64.30s - 67.58s]', 'text': "There's so much I about Terminator 2 1, it's exciting as hell."}, {'timestamp': '[67.58s - 71.06s]', 'text': "In the first movie, you have a soldier who's protecting Sarah Connor from a Terminator."}, {'timestamp': '[71.18s - 73.08s]', 'text': "So they can't really scrap in that movie."}, {'timestamp': '[73.18s - 76.36s]', 'text': 'A hand-to-hand fight will be Terminator going boom, dun dun dun dun.'}, {'timestamp': '[76.48s - 78.30s]', 'text': "Well, there's his head, , he's dead, I win."}, {'timestamp': '[78.42s - 82.74s]', 'text': "But in Terminator 2, you have Arnold Schwarzenegger, a T-800 machine, same model that's in Terminator"}, {'timestamp': '[82.88s - 85.64s]', 'text': '1, and you have Robert Patrick playing the T-1000.'}, {'timestamp': '[86.12s - 89.50s]', 'text': "So you can have them throw each other through walls and they're not gonna die from it."}, {'timestamp': '[89.52s - 91.28s]', 'text': "You're just gonna be absurdly entertained by it."}, {'timestamp': '[91.32s - 96.56s]', 'text': 'And as for the T-1000, the T-1000 in Terminator 2 remains one of the deadliest bastards ever'}, {'timestamp': '[96.68s - 97.26s]', 'text': 'put in a movie.'}, {'timestamp': '[97.38s - 101.10s]', 'text': 'This guy was just death incarnate and he was revolutionary for the time.'}, {'timestamp': '[101.24s - 104.42s]', 'text': "He's made completely out of liquid metal so he can change his appearance, he can look"}, {'timestamp': '[104.52s - 107.44s]', 'text': 'anyone, he can turn his arms into knives and stabbing weapons.'}, {'timestamp': '[107.60s - 109.87s]', 'text': "I know that is common, now you're , I've seen that before."}, {'timestamp': '[109.87s - 113.14s]', 'text': "But in 1991, that was absurd, that hadn't been done before."}, {'timestamp': '[113.32s - 116.40s]', 'text': 'After you watch Terminator 2 Judgment Day, T-1000 is in your mind.'}, {'timestamp': '[116.54s - 120.33s]', 'text': "You go to anyone and you're , oh, iconic T-1000 moment, they're , I have to pick one?"}, {'timestamp': '[120.33s - 124.17s]', 'text': "There's a scene where he gets frozen in liquid nitrogen, he's walking towards John Connor"}, {'timestamp': '[124.17s - 127.20s]', 'text': "and he's just not stopping but he's slowly freezing and Arnold's all ,"}, {'timestamp': '[129.04s - 131.44s]', 'text': "That's a staple cinema moment right there."}, {'timestamp': '[131.56s - 136.04s]', 'text': 'And what the T-1000 does in Terminator 2 remains to this day the coolest stuff any liquid metal'}, {'timestamp': '[136.18s - 137.38s]', 'text': 'being has ever done in a movie.'}, {'timestamp': '[137.50s - 141.54s]', 'text': 'And the excitement in this movie never stops, Arnold Schwarzenegger and T-1000 fight'}, {'timestamp': '[141.74s - 142.10s]', 'text': 'in a mall.'}, {'timestamp': '[142.64s - 146.24s]', 'text': "Then T-1000 chases John Connor on foot, then he gets in a semi and he's going after John"}, {'timestamp': '[146.28s - 147.50s]', 'text': 'Connor on his little motorcycle.'}, {'timestamp': '[147.76s - 151.42s]', 'text': "Then Arnold's pursuing the semi on his motorcycle trying to get to John Connor."}, {'timestamp': '[151.52s - 154.73s]', 'text': "That's just one of the many action sequences in Terminator 2 that are just , dude,"}, {'timestamp': '[154.73s - 155.50s]', 'text': "that's just the best."}, {'timestamp': '[155.68s - 159.98s]', 'text': 'And above it being exciting and having this revolutionary T-1000 character, the human'}, {'timestamp': '[160.10s - 161.46s]', 'text': 'characters themselves are deeper.'}, {'timestamp': '[161.62s - 165.60s]', 'text': "In Terminator 1, Kyle Reese, the soldier who's protecting Sarah Connor, kind of burdened"}, {'timestamp': '[165.60s - 168.72s]', 'text': 'her with knowledge and let her know that the human race is going to be incinerated and'}, {'timestamp': '[168.72s - 170.12s]', 'text': 'machines are going to take over the world.'}, {'timestamp': '[170.38s - 172.88s]', 'text': "And she let that slip to a few people, now people think she's crazy."}, {'timestamp': '[173.02s - 176.86s]', 'text': "So she's in a mental institution and she is not the Sarah Connor from Terminator 1."}, {'timestamp': '[176.98s - 180.76s]', 'text': "T-1000, she's Susie Homemaker, she's a waitress, she's , oh, I'm no one special."}, {'timestamp': '[181.04s - 184.50s]', 'text': "Now for the past decade, she's been training, doing pushups, becoming all hardcore."}, {'timestamp': '[184.80s - 186.70s]', 'text': "She's quite the badass in Terminator 2."}, {'timestamp': '[186.76s - 189.74s]', 'text': "She's not Susie Homemaker, she's Susie Kill You With My Pinkie."}, {'timestamp': '[189.78s - 190.52s]', 'text': "She's nuts, man."}, {'timestamp': '[190.64s - 194.58s]', 'text': "And in the world of Terminator 2 being a little deeper than you think it might be, there's"}, {'timestamp': '[194.58s - 198.38s]', 'text': "a scene where Sarah Connor learns about the guy who's going to ultimately cause Judgment"}, {'timestamp': '[198.46s - 198.60s]', 'text': 'Day.'}, {'timestamp': '[199.46s - 200.60s]', 'text': "And she's on a quest to wipe this guy out."}, {'timestamp': '[200.64s - 201.24s]', 'text': 'I mean, why not?'}, {'timestamp': '[201.26s - 202.86s]', 'text': 'She kills him, she changes the future.'}, {'timestamp': '[202.96s - 204.18s]', 'text': 'The robots never take over.'}, {'timestamp': '[204.30s - 206.84s]', 'text': "At that point, she's a Terminator to this guy."}, {'timestamp': '[206.98s - 210.46s]', 'text': "She might not be a machine the other Terminators, but she's on a quest to kill"}, {'timestamp': '[210.56s - 211.62s]', 'text': 'someone to change the future.'}, {'timestamp': '[211.76s - 213.12s]', 'text': 'I just, I that little detail.'}, {'timestamp': '[213.26s - 216.18s]', 'text': "And to any and all you girls out there who are , yeah, Terminator 2, I don't know,"}, {'timestamp': '[216.18s - 217.73s]', 'text': "it's just a Sky Movie, it's just a Sky Movie."}, {'timestamp': '[217.73s - 219.12s]', 'text': "Here's a story, true story."}, {'timestamp': '[219.24s - 220.82s]', 'text': 'I knew this girl who said the same thing.'}, {'timestamp': '[220.82s - 224.30s]', 'text': "She was , I have no interest in Terminator 2, it's a Sky Movie, what would I about"}, {'timestamp': '[224.30s - 224.50s]', 'text': 'it?'}, {'timestamp': '[224.96s - 228.42s]', 'text': 'I loaned her my copy, I was , watch it, I will bet you that you will love it, not'}, {'timestamp': '[228.46s - 230.78s]', 'text': 'only will you love it, you might even cry at the end.'}, {'timestamp': '[230.84s - 232.52s]', 'text': 'I still, dude, man tears at the end, seriously.'}, {'timestamp': '[232.52s - 234.76s]', 'text': 'She returned it, she was , oh my God, it was so good.'}, {'timestamp': '[234.84s - 236.26s]', 'text': 'You were just right, it was so good.'}, {'timestamp': '[236.32s - 238.49s]', 'text': "Yeah, I don't mess around about that shit."}, {'timestamp': '[238.49s - 241.28s]', 'text': 'Terminator 2 Judgment Day ends Terminator lore for me.'}, {'timestamp': '[241.36s - 243.96s]', 'text': 'The Terminator saga is Terminator 1 and Terminator 2.'}, {'timestamp': '[244.04s - 245.46s]', 'text': 'After that, nothing is canon.'}, {'timestamp': '[245.54s - 248.90s]', 'text': "It'll be light entertainment at best, but in the end, it ends at Terminator 2."}, {'timestamp': '[249.02s - 252.98s]', 'text': 'And in Terminator 2, being one of my favorite movies of all time, if I were to make a top'}, {'timestamp': '[253.02s - 255.14s]', 'text': '10 list, it has to be on there somewhere.'}, {'timestamp': '[255.70s - 258.84s]', 'text': 'Terminator 2 Judgment Day is awesome-tacular.'}, {'timestamp': '[263.92s - 267.60s]', 'text': 'If someone had a gun to my head and was , best Cameron movie ever, you have to say one,'}, {'timestamp': '[267.66s - 268.86s]', 'text': "I'd be , oh, T2, definitely."}, {'timestamp': '[269.04s - 271.14s]', 'text': "And I'm pretty sure I would live through the situation."}, {'timestamp': '[271.30s - 274.64s]', 'text': 'So your favorite Terminator movie out there, you gotta have one.'}, {'timestamp': '[274.84s - 275.38s]', 'text': 'What is it?'}, {'timestamp': '[275.52s - 276.88s]', 'text': 'Comment below, let me know.'}, {'timestamp': '[277.04s - 280.26s]', 'text': "And as always, if you what you've seen here and you want to see more, click right"}, {'timestamp': '[280.32s - 281.14s]', 'text': 'here to see more.'}, {'timestamp': '[281.28s - 282.88s]', 'text': 'Hasta la vista, baby.'}, {'timestamp': '[285.70s - 285.80s]', 'text': 'Bye.'}]
    visual_data= [{'timestamp': '[0.00s]', 'text': 'there is a man that is standing in the dark with a cell phone'}, {'timestamp': '[1.20s]', 'text': 'arafed man in a black shirt and black jacket making a gesture'}, {'timestamp': '[6.47s]', 'text': 'jeremy jahns presents the best of the best'}, {'timestamp': '[8.47s]', 'text': 'terminator 3 judgment day poster'}, {'timestamp': '[11.10s]', 'text': 'there is a man that is standing in the dark with a cell phone'}, {'timestamp': '[20.47s]', 'text': 'arafed man in a black shirt and black jacket making a stop sign'}, {'timestamp': '[22.57s]', 'text': 'arafed man in a black shirt and black jacket standing in front of a red background'}, {'timestamp': '[25.47s]', 'text': 'a close up of a man in a black shirt and a red background'}, {'timestamp': '[26.70s]', 'text': 'a man in a suit is holding a cell phone and a picture of a robot'}, {'timestamp': '[27.90s]', 'text': 'a close up of a man in a suit and tie standing in front of a red background'}, {'timestamp': '[28.87s]', 'text': 'a close up of a man in a suit and tie with a red background'}, {'timestamp': '[31.13s]', 'text': 'arafed man in a black shirt and black jacket standing in front of a red wall'}, {'timestamp': '[34.37s]', 'text': 'arafed man in a black shirt and black shirt holding a green object'}, {'timestamp': '[35.17s]', 'text': 'arafed image of a man in a black shirt and a red background'}, {'timestamp': '[40.87s]', 'text': 'a close up of a person with a hand up in front of a picture'}, {'timestamp': '[42.07s]', 'text': 'a close up of a person with a black shirt and a red background'}, {'timestamp': '[43.17s]', 'text': 'a close up of a man in a suit and sunglasses pointing at a picture'}, {'timestamp': '[43.80s]', 'text': 'arafed image of a man in a black shirt and a red background'}, {'timestamp': '[44.87s]', 'text': 'arafed image of a man in a suit with a speech bubble above his head'}, {'timestamp': '[45.70s]', 'text': 'arafed man in a black shirt and black jacket making a gesture'}, {'timestamp': '[47.47s]', 'text': 'arafed man in a black shirt and black jacket looking up'}, {'timestamp': '[53.03s]', 'text': 'arafed man in a black shirt and black jacket is making a funny face'}, {'timestamp': '[54.40s]', 'text': 'arafed image of a man with a black shirt and a red background'}, {'timestamp': '[55.10s]', 'text': 'a close up of a person pointing at a picture of a person'}, {'timestamp': '[57.57s]', 'text': 'arafed man in a black shirt and black jacket singing into a microphone'}, {'timestamp': '[59.47s]', 'text': 'a close up of a person in a suit and sunglasses'}, {'timestamp': '[64.40s]', 'text': 'arafed man in a black shirt and black jacket standing in front of a red wall'}, {'timestamp': '[71.40s]', 'text': 'arafed man in a black shirt and black shirt with fists up'}, {'timestamp': '[75.03s]', 'text': 'arafed man in a black shirt and black jacket holding a white object'}, {'timestamp': '[78.40s]', 'text': 'a close up of a man in a black shirt and a black jacket'}, {'timestamp': '[79.50s]', 'text': 'a close up of a person in a suit and sunglasses with a red background'}, {'timestamp': '[83.63s]', 'text': 'arafed image of a man in a black shirt and a red background'}, {'timestamp': '[89.47s]', 'text': 'arafed image of a man in a black shirt and black jacket'}, {'timestamp': '[91.27s]', 'text': 'arafed man in a black shirt and black jacket with a red background'}, {'timestamp': '[97.33s]', 'text': 'arafed image of a man in a black shirt and a red background'}, {'timestamp': '[101.20s]', 'text': 'a close up of a person with a video in front of a picture'}, {'timestamp': '[107.57s]', 'text': 'arafed man in a black shirt and black jacket singing into a microphone'}, {'timestamp': '[120.50s]', 'text': 'arafed man in a black shirt and black jacket is holding a video game controller'}, {'timestamp': '[127.20s]', 'text': 'arafed man in a black jacket pointing at the camera'}, {'timestamp': '[129.20s]', 'text': 'arafed man in a black shirt and black jacket is making a funny face'}, {'timestamp': '[131.50s]', 'text': 'arafed man in a black shirt and black jacket holding a cell phone'}, {'timestamp': '[135.77s]', 'text': 'arafed man in a black shirt and black jacket with his hands out'}, {'timestamp': '[137.47s]', 'text': 'arafed man in a black shirt and black jacket standing in front of a red background'}, {'timestamp': '[155.70s]', 'text': 'arafed man in a black shirt and black jacket singing into a microphone'}, {'timestamp': '[159.60s]', 'text': 'arafed man in a black shirt and black jacket is talking'}, {'timestamp': '[168.60s]', 'text': 'a close up of a person in a suit with a speech bubble above them'}, {'timestamp': '[170.20s]', 'text': 'arafed man in a black shirt and black jacket with his mouth open'}, {'timestamp': '[173.20s]', 'text': 'arafed man in a black shirt and black jacket making a face'}, {'timestamp': '[174.43s]', 'text': 'arafed man in a black shirt and black jacket pointing at something'}, {'timestamp': '[177.00s]', 'text': 'a close up of a man in a suit and a woman in a fur hat'}, {'timestamp': '[181.00s]', 'text': 'arafed image of a man in a black shirt and sunglasses'}, {'timestamp': '[184.77s]', 'text': 'a close up of a person on a motorcycle with a picture of a woman'}, {'timestamp': '[190.60s]', 'text': 'arafed man in a black shirt and black jacket making a funny face'}, {'timestamp': '[196.83s]', 'text': 'arafed man in a black shirt making a funny face'}, {'timestamp': '[204.23s]', 'text': 'arafed man in a black suit pointing at something'}, {'timestamp': '[210.20s]', 'text': 'arafed man in a black shirt and black jacket holding his hands up'}, {'timestamp': '[211.73s]', 'text': 'arafed man in a black shirt and black jacket holding a remote'}, {'timestamp': '[213.23s]', 'text': 'arafed man in a black shirt and black jacket singing into a microphone'}, {'timestamp': '[217.80s]', 'text': 'arafed man in a black shirt is making a gesture'}, {'timestamp': '[238.67s]', 'text': 'arafed man in a black shirt and black jacket holding a glass'}, {'timestamp': '[242.50s]', 'text': 'arafed man in a black shirt and black jacket making a stop sign'}, {'timestamp': '[248.93s]', 'text': 'arafed man in a black shirt and black jacket making a funny face'}, {'timestamp': '[256.73s]', 'text': 'terminator 2 judgment day movie poster'}, {'timestamp': '[263.90s]', 'text': 'arafed image of a man in a black shirt and black jacket'}, {'timestamp': '[267.67s]', 'text': 'a man in a black shirt and black jacket holding a gun'}, {'timestamp': '[271.23s]', 'text': 'arafed man in a black shirt and black jacket holding a red object'}, {'timestamp': '[275.43s]', 'text': 'arafed man in a black shirt and black jacket pointing at something'}, {'timestamp': '[277.00s]', 'text': 'arafed man in black shirt making a funny face with his hands'}, {'timestamp': '[281.23s]', 'text': 'arafed man in a black jacket pointing at the camera'}, {'timestamp': '[283.23s]', 'text': 'there is a man pointing at the camera with a red background'}, {'timestamp': '[283.93s]', 'text': 'a close up of a person holding a cell phone in front of a sign'}]    
    # Learning Method B
    audio_res, visual_res, total_duration = teaser_pipeline("learning_b", audio_data=audio_data, visual_data=visual_data)
    print("Learning Method B - Audio Results:", audio_res)
    print("Learning Method B - Visual Results:", visual_res)
    print("Total Duration:", total_duration)