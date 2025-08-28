import re

def extract_timestamps_by_method(method, audio_results, visual_results):
    """
    Extract timestamps based on method type.
    
    Args:
        method (str): 'Learning Method A', 'Learning Method B', or 'Cinematic Method A'
        audio_results (list): [{'timestamp': '[x.xx - y.yy]', 'text': '...'}]
        visual_results (list): [{'timestamp': '[x.xx]', 'text': '...'}]
    
    Returns:
        list: [[start, end], ...]
    """
    method = method.strip().lower()
    timestamps = []

    # Function to extract audio timestamps
    def get_audio():
        ts = []
        for item in audio_results:
            match = re.findall(r"[\d.]+", item['timestamp'])
            if len(match) == 2:
                start, end = map(float, match)
                ts.append([start, end])
        return ts

    # Function to extract visual timestamps
    def get_visual():
        ts = []
        for item in visual_results:
            match = re.findall(r"[\d.]+", item['timestamp'])
            if len(match) == 1:
                start = float(match[0])
                ts.append([start, start + 1.5])
        return ts

    if method == "learning method a":
        timestamps = get_audio()
    elif method in ["learning method b", "cinematic method a"]:
        timestamps = get_visual()
    else:
        raise ValueError(f"Unknown method: {method}")

    # Sort timestamps by start time
    return timestamps


audio_data = [{'timestamp': '[238.49s - 241.28s]', 'text': 'Terminator 2 Judgment Day ends Terminator lore for me.'}, {'timestamp': '[142.64s - 146.24s]', 'text': "Then T-1000 chases John Connor on foot, then he gets in a semi and he's going after John"}, {'timestamp': '[73.18s - 76.36s]', 'text': 'A hand-to-hand fight will be Terminator going boom, dun dun dun dun.'}, {'timestamp': '[249.02s - 252.98s]', 'text': 'And in Terminator 2, being one of my favorite movies of all time, if I were to make a top'}, {'timestamp': '[165.60s - 168.72s]', 'text': 'her with knowledge and let her know that the human race is going to be incinerated and'}, {'timestamp': '[64.30s - 67.58s]', 'text': "There's so much I about Terminator 2 1, it's exciting as hell."}, {'timestamp': '[245.54s - 248.90s]', 'text': "It'll be light entertainment at best, but in the end, it ends at Terminator 2."}, {'timestamp': '[155.68s - 159.98s]', 'text': 'And above it being exciting and having this revolutionary T-1000 character, the human'}, {'timestamp': '[96.68s - 97.26s]', 'text': 'put in a movie.'}, {'timestamp': '[11.52s - 13.16s]', 'text': 'Terminator 2, Judgment Day.'}, {'timestamp': '[263.92s - 267.60s]', 'text': 'If someone had a gun to my head and was , best Cameron movie ever, you have to say one,'}, {'timestamp': '[271.30s - 274.64s]', 'text': 'So your favorite Terminator movie out there, you gotta have one.'}, {'timestamp': '[116.54s - 120.33s]', 'text': "You go to anyone and you're , oh, iconic T-1000 moment, they're , I have to pick one?"}]

visual_data = [{'timestamp': '[22.57s]', 'text': 'arafed man in a black shirt and black jacket standing in front of a red background'}, {'timestamp': '[137.47s]', 'text': 'arafed man in a black shirt and black jacket standing in front of a red background'}, {'timestamp': '[47.47s]', 'text': 'arafed man in a black shirt and black jacket looking up'}, {'timestamp': '[53.03s]', 'text': 'arafed man in a black shirt and black jacket is making a funny face'}, {'timestamp': '[129.20s]', 'text': 'arafed man in a black shirt and black jacket is making a funny face'}, {'timestamp': '[204.23s]', 'text': 'arafed man in a black suit pointing at something'}, {'timestamp': '[27.90s]', 'text': 'a close up of a man in a suit and tie standing in front of a red background'}, {'timestamp': '[35.17s]', 'text': 'arafed image of a man in a black shirt and a red background'}, {'timestamp': '[43.80s]', 'text': 'arafed image of a man in a black shirt and a red background'}, {'timestamp': '[83.63s]', 'text': 'arafed image of a man in a black shirt and a red background'}, {'timestamp': '[97.33s]', 'text': 'arafed image of a man in a black shirt and a red background'}, {'timestamp': '[40.87s]', 'text': 'a close up of a person with a hand up in front of a picture'}, {'timestamp': '[54.40s]', 'text': 'arafed image of a man with a black shirt and a red background'}, {'timestamp': '[101.20s]', 'text': 'a close up of a person with a video in front of a picture'}, {'timestamp': '[43.17s]', 'text': 'a close up of a man in a suit and sunglasses pointing at a picture'}, {'timestamp': '[44.87s]', 'text': 'arafed image of a man in a suit with a speech bubble above his head'}, {'timestamp': '[256.73s]', 'text': 'terminator 2 judgment day movie poster'}, {'timestamp': '[6.47s]', 'text': 'jeremy jahns presents the best of the best'}, {'timestamp': '[8.47s]', 'text': 'terminator 3 judgment day poster'}]
# Example 1: Learning Method A → use audio timestamps
#print(extract_timestamps_by_method("Learning Method A", audio_data, visual_data))
# Output: [[11.52, 13.16], [96.68, 97.26], [238.49, 241.28]]

# Example 2: Learning Method B → use visual timestamps
print(extract_timestamps_by_method("Learning Method B", audio_data, visual_data))
# Output: [[22.73, 24.23], [61.47, 62.97]]

# Example 3: Cinematic Method A → also use visual timestamps
#print(extract_timestamps_by_method("Cinematic Method A", audio_data, visual_data))
# Output: [[22.73, 24.23], [61.47, 62.97]]
