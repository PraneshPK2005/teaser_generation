import re
from itertools import groupby


# -------------------------------
# Visual Preprocessing
# -------------------------------
def preprocess_visual(visual_descriptions):
    """
    Preprocess visual descriptions by removing filler phrases and consecutive duplicates.
    
    Args:
        visual_descriptions (list): List of visual description strings with timestamps
    
    Returns:
        list: List of dictionaries with 'timestamp' and 'text' keys
    """
    
    def clean_text(text):
        # Remove unwanted filler phrases
        patterns = [
            r'^there is (a|an)?\s?',
            r'^there are ',
            r'^a close up of ',
            r'^a picture of ',
            r'^arafed\s?',
            r'^araffes\s?'
        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    cleaned = []
    for t in visual_descriptions:
        try:
            timestamp, text = t.split(']', 1)
            timestamp = timestamp + ']'  # add closing bracket
            text = clean_text(text)
            cleaned.append({"timestamp": timestamp, "text": text})
        except ValueError:
            continue  # skip malformed entries
    
    # Remove consecutive duplicates
    unique = [next(group) for _, group in groupby(cleaned, key=lambda x: x["text"])]
    
    return unique


if __name__ == "__main__":
    visual_descriptions = ['[0.00s] there is a man that is standing in the dark with a cell phone', '[1.20s] arafed man in a black shirt and black jacket making a gesture', '[6.47s] jeremy jahns presents the best of the best', '[8.47s] terminator 3 judgment day poster', '[11.10s] there is a man that is standing in the dark with a cell phone', '[20.47s] arafed man in a black shirt and black jacket making a stop sign', '[22.57s] arafed man in a black shirt and black jacket standing in front of a red background', '[25.47s] a close up of a man in a black shirt and a red background', '[26.70s] a man in a suit is holding a cell phone and a picture of a robot', '[27.90s] a close up of a man in a suit and tie standing in front of a red background', '[28.87s] a close up of a man in a suit and tie with a red background', '[31.13s] arafed man in a black shirt and black jacket standing in front of a red wall', '[34.37s] arafed man in a black shirt and black shirt holding a green object', '[35.17s] arafed image of a man in a black shirt and a red background', '[40.87s] a close up of a person with a hand up in front of a picture', '[42.07s] a close up of a person with a black shirt and a red background', '[43.17s] a close up of a man in a suit and sunglasses pointing at a picture', '[43.80s] arafed image of a man in a black shirt and a red background', '[44.87s] arafed image of a man in a suit with a speech bubble above his head', '[45.70s] arafed man in a black shirt and black jacket making a gesture', '[47.47s] arafed man in a black shirt and black jacket looking up', '[53.03s] arafed man in a black shirt and black jacket is making a funny face', '[54.40s] arafed image of a man with a black shirt and a red background', '[55.10s] a close up of a person pointing at a picture of a person', '[57.57s] arafed man in a black shirt and black jacket singing into a microphone', '[59.47s] a close up of a person in a suit and sunglasses', '[64.40s] arafed man in a black shirt and black jacket standing in front of a red wall', '[71.40s] arafed man in a black shirt and black shirt with fists up', '[75.03s] arafed man in a black shirt and black jacket holding a white object', '[78.40s] a close up of a man in a black shirt and a black jacket', '[79.50s] a close up of a person in a suit and sunglasses with a red background', '[83.63s] arafed image of a man in a black shirt and a red background', '[86.10s] arafed image of a man in a black shirt and a red background', '[89.47s] arafed image of a man in a black shirt and black jacket', '[91.27s] arafed man in a black shirt and black jacket with a red background', '[97.33s] arafed image of a man in a black shirt and a red background', '[101.20s] a close up of a person with a video in front of a picture', '[107.57s] arafed man in a black shirt and black jacket singing into a microphone', '[120.50s] arafed man in a black shirt and black jacket is holding a video game controller', '[127.20s] arafed man in a black jacket pointing at the camera', '[129.20s] arafed man in a black shirt and black jacket is making a funny face', '[131.50s] arafed man in a black shirt and black jacket holding a cell phone', '[135.77s] arafed man in a black shirt and black jacket with his hands out', '[137.47s] arafed man in a black shirt and black jacket standing in front of a red background', '[155.70s] arafed man in a black shirt and black jacket singing into a microphone', '[159.60s] arafed man in a black shirt and black jacket is talking', '[168.60s] a close up of a person in a suit with a speech bubble above them', '[170.20s] arafed man in a black shirt and black jacket with his mouth open', '[173.20s] arafed man in a black shirt and black jacket making a face', '[174.43s] arafed man in a black shirt and black jacket pointing at something', '[177.00s] a close up of a man in a suit and a woman in a fur hat', '[181.00s] arafed image of a man in a black shirt and sunglasses', '[184.77s] a close up of a person on a motorcycle with a picture of a woman', '[190.60s] arafed man in a black shirt and black jacket making a funny face', '[196.83s] arafed man in a black shirt making a funny face', '[204.23s] arafed man in a black suit pointing at something', '[210.20s] arafed man in a black shirt and black jacket holding his hands up', '[211.73s] arafed man in a black shirt and black jacket holding a remote', '[213.23s] arafed man in a black shirt and black jacket singing into a microphone', '[217.80s] arafed man in a black shirt is making a gesture', '[238.67s] arafed man in a black shirt and black jacket holding a glass', '[242.50s] arafed man in a black shirt and black jacket making a stop sign', '[248.93s] arafed man in a black shirt and black jacket making a funny face', '[256.73s] terminator 2 judgment day movie poster', '[263.90s] arafed image of a man in a black shirt and black jacket', '[267.67s] a man in a black shirt and black jacket holding a gun', '[271.23s] arafed man in a black shirt and black jacket holding a red object', '[275.43s] arafed man in a black shirt and black jacket pointing at something', '[277.00s] arafed man in black shirt making a funny face with his hands', '[281.23s] arafed man in a black jacket pointing at the camera', '[283.23s] there is a man pointing at the camera with a red background', '[283.93s] a close up of a person holding a cell phone in front of a sign']
        
    visual_data = preprocess_visual(visual_descriptions)
    print(visual_data)