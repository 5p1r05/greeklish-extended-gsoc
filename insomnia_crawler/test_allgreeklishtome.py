# Calculate scores for misaligned texts
import re
import allgreek2me_master.greeklish as greeklish
import os 
import json


def detect_language(text):
    """
    Checks whether the majority of the letters in the input text are in the greek or the latin script
    It is used to identify whether the text is in greek or greeklish (latin script), in order to skip unnecessary conversions.

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
    
    if(greek_count == 0 and english_count == 0):
        return "unknown"

    script = "greek" if greek_count >= english_count else "latin"
    return script

def calculate_scores_misaligned(original_text, predicted_text, gt_indices):
    TP = 0
    FP = 0
    FN = 0

    indices_not_found = []
    for index in gt_indices:
        word = original_text.split(" ")[index]
        # Check whether the word is in the predicted text
        if(word in predicted_text or word.lower() in predicted_text or word.upper() in predicted_text):
            TP += 1
        # If the word is not in the predicted text, it is a false negative
        else:
            FN += 1
            indices_not_found.append(index)

    # Check for false positives

    original_english_words = [original_text.split(" ")[index] for index in gt_indices]
    for i, word in enumerate(predicted_text.split(" ")):
        # only keep the letters
        stripped_word = " ".join(re.findall("[a-zA-Z]+", word))
        if detect_language(stripped_word) == "latin":
            if(word not in original_english_words and word.lower() not in original_english_words and word.upper() not in original_english_words):
                FP += 1
    
    return TP, FP, FN



g2g = greeklish.GreeklishConverter()


forum_names = os.listdir("forums_info/forums_sampled/")

precisions = []
recalls = []

TP_all = 0
FP_all = 0
FN_all = 0


for forum_name in forum_names:
    with open(f"forums_info/forums_sampled/{forum_name}", "r") as f:
        forum_data = json.load(f)

    print(f"Forum: {forum_name}")
    for c, comment in enumerate(forum_data):
        greek_text = g2g.convert(comment["text"])
        TP, FP, FN = calculate_scores_misaligned(comment["text"], greek_text, comment["gt_indices"])
        
        # skip if the denominator is 0
        if(TP + FN == 0 or TP + FP == 0):
            continue

        TP_all += TP
        FP_all += FP
        FN_all += FN

        recall = TP / (TP + FN)
        precision = TP / (TP + FP)
        
        precisions.append(precision)
        recalls.append(recall)


print(f"Average macro precision: {sum(precisions) / len(precisions):.2f}")
print(f"Average macro recall: {sum(recalls) / len(recalls):.2f}")

micro_average_precision = TP_all / (TP_all + FP_all)
micro_average_recall = TP_all / (TP_all + FN_all)

print(f"Average micro precision: {micro_average_precision:.2f}")
print(f"Average micro recall: {micro_average_recall:.2f}")