import ollama
import pyttsx3
import os

def summarize_text(transcript, duration_seconds, wpm, model='llama3.2:latest'):
    """
    Summarizes a transcript to a specific word count based on duration and WPM using an Ollama model.

    Args:
        transcript (str): The long text to be summarized.
        duration_seconds (int): The target duration of the final audio in seconds.
        wpm (int): The desired words per minute for the summary's reading pace.
        model (str): The name of the Ollama model to use (e.g., 'llama3', 'mistral').

    Returns:
        str: The summarized text, or None if an error occurs.
    """
    if not transcript:
        print("Error: The input transcript cannot be empty.")
        return None

    # 1. Calculate the target word count to guide the model
    target_word_count = int((duration_seconds / 60) * wpm)
    print(f"Targeting a summary of approximately {target_word_count} words.")

    # 2. Create a more descriptive prompt for the Ollama model
    # --- MODIFIED PROMPT ---
    prompt = f"""
    Your task is to summarize the following transcript.
    The final summary must be a specific length so that when it is read aloud at a pace of {wpm} words per minute, the total duration is exactly {duration_seconds} seconds.

    Based on this, the summary should be approximately {target_word_count} words long. Please generate a concise and natural-sounding summary that fits these constraints.
    Do not add any extra text, titles, or introductions.

    TRANSCRIPT:
    ---
    {transcript}
    ---
    """

    try:
        print(f"Sending request to Ollama model '{model}'...")
        # 3. Call the Ollama API
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'user', 'content': prompt},
            ],
            options={
                "num_ctx": 100000  # or higher, depending on what llama3.2:3b supports
            }
        )
        summary = response['message']['content'].strip()
        actual_word_count = len(summary.split())
        print(f"Ollama generated a summary of {actual_word_count} words.")
        return summary
    except Exception as e:
        print(f"An error occurred while contacting Ollama: {e}")
        return None
    
def create_timed_audio(text, duration_seconds, filename="summary_audio.mp3"):
    """
    Generates an audio file from text that precisely matches a target duration.

    Args:
        text (str): The text to convert to speech (the summary).
        duration_seconds (int): The target duration of the audio in seconds.
        filename (str): The name of the output audio file.
    """
    if not text:
        print("Error: No text provided for audio generation.")
        return

    try:
        # 1. Calculate the required WPM to fit the text into the duration
        actual_word_count = len(text.split())
        
        # Calculate the base WPM and then increase it by 5% (multiply by 1.05)
        # --- MODIFIED LINE ---
        required_wpm = ((actual_word_count * 60) / duration_seconds) * 1.05
        
        print("\n--- Audio Generation ---")
        print(f"Syncing {actual_word_count} words into {duration_seconds} seconds.")
        print(f"Required audio speaking rate (adjusted +5%): {required_wpm:.2f} WPM")

        # 2. Generate the audio using a fresh pyttsx3 engine
        engine = pyttsx3.init()
        engine.setProperty('rate', required_wpm)
        engine.save_to_file(text, filename)
        engine.runAndWait()

        if os.path.exists(filename):
            print(f"✅ Successfully created synchronized audio file: '{filename}'")
        else:
            print("❌ Failed to create audio file.")
            
    except Exception as e:
        print(f"An error occurred during audio generation: {e}")
# --- Main Execution ---
if __name__ == "__main__":

        # The transcript data you provided
    transcript_data = [
        {'timestamp': '[0.00s - 4.23s]', 'text': "Not only am I going to review an older movie for you guys, but I'm going to review one"},
        {'timestamp': '[4.23s - 6.22s]', 'text': 'of my favorite movies, as in , ever.'},
        {'timestamp': '[11.52s - 13.16s]', 'text': 'Terminator 2, Judgment Day.'},
        {'timestamp': '[13.24s - 15.90s]', 'text': "I know what some of you are thinking right now, you're , wait, Terminator 2, where's"},
        {'timestamp': '[15.90s - 16.58s]', 'text': 'Terminator 1?'},
        {'timestamp': '[16.72s - 19.60s]', 'text': 'I wanted to go straight for the throat on this one, I wanted to review one of my favorite'},
        {'timestamp': '[19.68s - 20.40s]', 'text': 'movies of all time.'},
        {'timestamp': '[20.46s - 22.32s]', 'text': "But I'm not going to leave you hanging, here's a bit of the backstory."},
        {'timestamp': '[22.40s - 27.47s]', 'text': 'In Terminator Lore, on August 29th, 1997, the machines we created became self-aware and'},
        {'timestamp': '[27.47s - 28.66s]', 'text': 'they pretty much wiped out mankind.'},
        {'timestamp': '[28.94s - 31.02s]', 'text': ", yeah, that didn't quite happen, but ."},
        {'timestamp': '[31.20s - 35.00s]', 'text': "From that point of the year, 2029, mankind's been locked in a war with the machines."},
        {'timestamp': '[35.18s - 38.60s]', 'text': 'The leader of this resistance is a man named John Conner and he leads mankind'},
        {'timestamp': '[38.66s - 39.16s]', 'text': 'to victory.'},
        {'timestamp': '[39.34s - 42.72s]', 'text': 'So in Terminator 1, the machines send a machine back in time to kill Sarah Connor.'},
        {'timestamp': '[42.82s - 45.58s]', 'text': 'Yeah, no Sarah Connor means no John Connor means the machines win.'},
        {'timestamp': '[45.76s - 47.34s]', 'text': 'And now we reach Terminator 2.'},
        {'timestamp': '[47.50s - 51.14s]', 'text': 'Machines kinda had to failsafe, they sent two Terminators back through time, one'},
        {'timestamp': '[51.18s - 55.04s]', 'text': 'back to the 80s to take out Sarah Connor, the other to the 90s to take out John Connor.'},
        {'timestamp': '[55.14s - 57.40s]', 'text': "But don't worry, we humans were smart and we have a plan."},
        {'timestamp': '[57.82s - 62.04s]', 'text': 'John Connor from the future reprograms the Terminator to protect him as a child in the 90s.'},
        {'timestamp': '[62.18s - 64.20s]', 'text': "Now we have our movie and it's awesome."},
        {'timestamp': '[64.30s - 67.58s]', 'text': "There's so much I about Terminator 2 1, it's exciting as hell."},
        {'timestamp': '[67.58s - 71.06s]', 'text': "In the first movie, you have a soldier who's protecting Sarah Connor from a Terminator."},
        {'timestamp': '[71.18s - 73.08s]', 'text': "So they can't really scrap in that movie."},
        {'timestamp': '[73.18s - 76.36s]', 'text': 'A hand-to-hand fight will be Terminator going boom, dun dun dun dun.'},
        {'timestamp': '[76.48s - 78.30s]', 'text': "Well, there's his head, , he's dead, I win."},
        {'timestamp': '[78.42s - 82.74s]', 'text': "But in Terminator 2, you have Arnold Schwarzenegger, a T-800 machine, same model that's in Terminator"},
        {'timestamp': '[82.88s - 85.64s]', 'text': '1, and you have Robert Patrick playing the T-1000.'},
        {'timestamp': '[86.12s - 89.50s]', 'text': "So you can have them throw each other through walls and they're not gonna die from it."},
        {'timestamp': '[89.52s - 91.28s]', 'text': "You're just gonna be absurdly entertained by it."},
        {'timestamp': '[91.32s - 96.56s]', 'text': 'And as for the T-1000, the T-1000 in Terminator 2 remains one of the deadliest bastards ever'},
        {'timestamp': '[96.68s - 97.26s]', 'text': 'put in a movie.'},
        {'timestamp': '[97.38s - 101.10s]', 'text': 'This guy was just death incarnate and he was revolutionary for the time.'},
        {'timestamp': '[101.24s - 104.42s]', 'text': "He's made completely out of liquid metal so he can change his appearance, he can look"},
        {'timestamp': '[104.52s - 107.44s]', 'text': 'anyone, he can turn his arms into knives and stabbing weapons.'},
        {'timestamp': '[107.60s - 109.87s]', 'text': "I know that is common, now you're , I've seen that before."},
        {'timestamp': '[109.87s - 113.14s]', 'text': "But in 1991, that was absurd, that hadn't been done before."},
        {'timestamp': '[113.32s - 116.40s]', 'text': 'After you watch Terminator 2 Judgment Day, T-1000 is in your mind.'},
        {'timestamp': '[116.54s - 120.33s]', 'text': "You go to anyone and you're , oh, iconic T-1000 moment, they're , I have to pick one?"},
        {'timestamp': '[120.33s - 124.17s]', 'text': "There's a scene where he gets frozen in liquid nitrogen, he's walking towards John Connor"},
        {'timestamp': '[124.17s - 127.20s]', 'text': "and he's just not stopping but he's slowly freezing and Arnold's all ,"},
        {'timestamp': '[129.04s - 131.44s]', 'text': "That's a staple cinema moment right there."},
        {'timestamp': '[131.56s - 136.04s]', 'text': 'And what the T-1000 does in Terminator 2 remains to this day the coolest stuff any liquid metal'},
        {'timestamp': '[136.18s - 137.38s]', 'text': 'being has ever done in a movie.'},
        {'timestamp': '[137.50s - 141.54s]', 'text': 'And the excitement in this movie never stops, Arnold Schwarzenegger and T-1000 fight'},
        {'timestamp': '[141.74s - 142.10s]', 'text': 'in a mall.'},
        {'timestamp': '[142.64s - 146.24s]', 'text': "Then T-1000 chases John Connor on foot, then he gets in a semi and he's going after John"},
        {'timestamp': '[146.28s - 147.50s]', 'text': 'Connor on his little motorcycle.'},
        {'timestamp': '[147.76s - 151.42s]', 'text': "Then Arnold's pursuing the semi on his motorcycle trying to get to John Connor."},
        {'timestamp': '[151.52s - 154.73s]', 'text': "That's just one of the many action sequences in Terminator 2 that are just , dude,"},
        {'timestamp': '[154.73s - 155.50s]', 'text': "that's just the best."},
        {'timestamp': '[155.68s - 159.98s]', 'text': 'And above it being exciting and having this revolutionary T-1000 character, the human'},
        {'timestamp': '[160.10s - 161.46s]', 'text': 'characters themselves are deeper.'},
        {'timestamp': '[161.62s - 165.60s]', 'text': "In Terminator 1, Kyle Reese, the soldier who's protecting Sarah Connor, kind of burdened"},
        {'timestamp': '[165.60s - 168.72s]', 'text': 'her with knowledge and let her know that the human race is going to be incinerated and'},
        {'timestamp': '[168.72s - 170.12s]', 'text': 'machines are going to take over the world.'},
        {'timestamp': '[170.38s - 172.88s]', 'text': "And she let that slip to a few people, now people think she's crazy."},
        {'timestamp': '[173.02s - 176.86s]', 'text': "So she's in a mental institution and she is not the Sarah Connor from Terminator 1."},
        {'timestamp': '[176.98s - 180.76s]', 'text': "T-1000, she's Susie Homemaker, she's a waitress, she's , oh, I'm no one special."},
        {'timestamp': '[181.04s - 184.50s]', 'text': "Now for the past decade, she's been training, doing pushups, becoming all hardcore."},
        {'timestamp': '[184.80s - 186.70s]', 'text': "She's quite the badass in Terminator 2."},
        {'timestamp': '[186.76s - 189.74s]', 'text': "She's not Susie Homemaker, she's Susie Kill You With My Pinkie."},
        {'timestamp': '[189.78s - 190.52s]', 'text': "She's nuts, man."},
        {'timestamp': '[190.64s - 194.58s]', 'text': "And in the world of Terminator 2 being a little deeper than you think it might be, there's"},
        {'timestamp': '[194.58s - 198.38s]', 'text': "a scene where Sarah Connor learns about the guy who's going to ultimately cause Judgment"},
        {'timestamp': '[198.46s - 198.60s]', 'text': 'Day.'},
        {'timestamp': '[199.46s - 200.60s]', 'text': "And she's on a quest to wipe this guy out."},
        {'timestamp': '[200.64s - 201.24s]', 'text': 'I mean, why not?'},
        {'timestamp': '[201.26s - 202.86s]', 'text': 'She kills him, she changes the future.'},
        {'timestamp': '[202.96s - 204.18s]', 'text': 'The robots never take over.'},
        {'timestamp': '[204.30s - 206.84s]', 'text': "At that point, she's a Terminator to this guy."},
        {'timestamp': '[206.98s - 210.46s]', 'text': "She might not be a machine the other Terminators, but she's on a quest to kill"},
        {'timestamp': '[210.56s - 211.62s]', 'text': 'someone to change the future.'},
        {'timestamp': '[211.76s - 213.12s]', 'text': 'I just, I that little detail.'},
        {'timestamp': '[213.26s - 216.18s]', 'text': "And to any and all you girls out there who are , yeah, Terminator 2, I don't know,"},
        {'timestamp': '[216.18s - 217.73s]', 'text': "it's just a Sky Movie, it's just a Sky Movie."},
        {'timestamp': '[217.73s - 219.12s]', 'text': "Here's a story, true story."},
        {'timestamp': '[219.24s - 220.82s]', 'text': 'I knew this girl who said the same thing.'},
        {'timestamp': '[220.82s - 224.30s]', 'text': "She was , I have no interest in Terminator 2, it's a Sky Movie, what would I about"},
        {'timestamp': '[224.30s - 224.50s]', 'text': 'it?'},
        {'timestamp': '[224.96s - 228.42s]', 'text': 'I loaned her my copy, I was , watch it, I will bet you that you will love it, not'},
        {'timestamp': '[228.46s - 230.78s]', 'text': 'only will you love it, you might even cry at the end.'},
        {'timestamp': '[230.84s - 232.52s]', 'text': 'I still, dude, man tears at the end, seriously.'},
        {'timestamp': '[232.52s - 234.76s]', 'text': 'She returned it, she was , oh my God, it was so good.'},
        {'timestamp': '[234.84s - 236.26s]', 'text': 'You were just right, it was so good.'},
        {'timestamp': '[236.32s - 238.49s]', 'text': "Yeah, I don't mess around about that shit."},
        {'timestamp': '[238.49s - 241.28s]', 'text': 'Terminator 2 Judgment Day ends Terminator lore for me.'},
        {'timestamp': '[241.36s - 243.96s]', 'text': 'The Terminator saga is Terminator 1 and Terminator 2.'},
        {'timestamp': '[244.04s - 245.46s]', 'text': 'After that, nothing is canon.'},
        {'timestamp': '[245.54s - 248.90s]', 'text': "It'll be light entertainment at best, but in the end, it ends at Terminator 2."},
        {'timestamp': '[249.02s - 252.98s]', 'text': 'And in Terminator 2, being one of my favorite movies of all time, if I were to make a top'},
        {'timestamp': '[253.02s - 255.14s]', 'text': '10 list, it has to be on there somewhere.'},
        {'timestamp': '[255.70s - 258.84s]', 'text': 'Terminator 2 Judgment Day is awesome-tacular.'},
        {'timestamp': '[263.92s - 267.60s]', 'text': 'If someone had a gun to my head and was , best Cameron movie ever, you have to say one,'},
        {'timestamp': '[267.66s - 268.86s]', 'text': "I'd be , oh, T2, definitely."},
        {'timestamp': '[269.04s - 271.14s]', 'text': "And I'm pretty sure I would live through the situation."},
        {'timestamp': '[271.30s - 274.64s]', 'text': 'So your favorite Terminator movie out there, you gotta have one.'},
        {'timestamp': '[274.84s - 275.38s]', 'text': 'What is it?'},
        {'timestamp': '[275.52s - 276.88s]', 'text': 'Comment below, let me know.'},
        {'timestamp': '[277.04s - 280.26s]', 'text': "And as always, if you what you've seen here and you want to see more, click right"},
        {'timestamp': '[280.32s - 281.14s]', 'text': 'here to see more.'},
        {'timestamp': '[281.28s - 282.88s]', 'text': 'Hasta la vista, baby.'},
        {'timestamp': '[285.70s - 285.80s]', 'text': 'Bye.'}
    ]

    text_snippets = [item['text'] for item in transcript_data]
    full_transcript = ' '.join(text_snippets)
    # Define your target duration and desired reading pace
    TARGET_DURATION_SECONDS = 120
    TARGET_WPM = 140
    # Paste your long transcript here
    LONG_TRANSCRIPT = full_transcript

    # Step 1: Summarize the text to the calculated length
    summary_text = summarize_text(
        transcript=LONG_TRANSCRIPT,
        duration_seconds=TARGET_DURATION_SECONDS,
        wpm=TARGET_WPM
    )

    # Step 2: Convert the summary to audio with the exact duration
    if summary_text:
        create_timed_audio(
            text=summary_text,
            duration_seconds=TARGET_DURATION_SECONDS
        )