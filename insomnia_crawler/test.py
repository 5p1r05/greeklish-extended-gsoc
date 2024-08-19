txt = "Επίσης έχει κάποια παιχνίδια με 3 ευρώ,μερικά αξίζουν πραγματικά. (dantes inferno,mass effect 2,bioschock 2)"

def dominant_language(text):
    """
    Checks whether the majority of the letters in the input text are in the greek or the latin script

    Args:
        text (str): The input text

    Returns:
        script (str): The dominant script
    """
    # Filter out non-letter characters
    valid_characters = [char for char in text if char.isalpha()]
    
    # Count Greek and English letters
    greek_count = sum(1 for char in valid_characters if '\u0370' <= char <= '\u03FF' or '\u1F00' <= char <= '\u1FFF')
    english_count = sum(1 for char in valid_characters if '\u0041' <= char <= '\u005A' or '\u0061' <= char <= '\u007A')
    
    all_count = greek_count + english_count

    # print("all count")
    # print(all_count)
    # print(0.8 * all_count)

    # print("greek count")
    # print(greek_count)

    # print("english count")
    # print(english_count)

    if all_count * 0.8 > english_count:
        return "latin"
    elif all_count * 0.8 > greek_count:
        return "greek" 

# print(dominant_language(txt))

