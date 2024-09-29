import allgreek2me_master.greeklish as greeklish
from sklearn.metrics import f1_score, precision_score, recall_score

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
    
    script = "greek" if greek_count >= english_count else "latin"
    return script

def calculate_scores(ground_truth, prediction):
    # Convert lists to sets
    ground_truth_set = set(ground_truth)
    prediction_set = set(prediction)

    # Combine all possible labels
    all_labels = list(ground_truth_set | prediction_set)

    # Convert sets to binary format for comparison
    ground_truth_binary = [int(label in ground_truth_set) for label in all_labels]
    prediction_binary = [int(label in prediction_set) for label in all_labels]

    # Calculate precision, recall, and F1 score
    precision = precision_score(ground_truth_binary, prediction_binary, zero_division=0)
    recall = recall_score(ground_truth_binary, prediction_binary, zero_division=0)
    # f1 = f1_score(ground_truth_binary, prediction_binary)

    return precision, recall

g2g = greeklish.GreeklishConverter()

forum_names = os.listdir("forums_info/forums_sampled/")

precisions = []
recalls = []

predicted_not_in_gts_all = []
gt_not_in_predicted_all = []

all_predicted = []
all_gt = []

for forum_name in forum_names:
    with open(f"forums_info/forums_sampled/{forum_name}", "r") as f:
        forum_data = json.load(f)

        print(f"Forum: {forum_name}")
        for c, comment in enumerate(forum_data):
            greek_text = g2g.convert(comment["text"])
            greek_text_split = greek_text.split(" ")

            # Save the indices of the english words within the greek text
            english_words_indices = []
            for i, word in enumerate(greek_text_split):
                if detect_language(word) == "latin":
                    english_words_indices.append(i)
            
            precision, recall = calculate_scores(comment["gt_indices"], english_words_indices)
            
            precisions.append(precision)
            recalls.append(recall)
            
            # Add the 
            # Determine which words were misclassified
            predicted_set = set(english_words_indices)
            gt_set = set(comment["gt_indices"])

            predicted_not_in_gt_indices = predicted_set - gt_set
            gt_not_in_predicted_indices = gt_set - predicted_set


            predicted_not_in_gt = [(comment['text'].split(" ")[index], c, index) for index in predicted_not_in_gt_indices]
            gt_not_in_predicted = [(comment['text'].split(" ")[index], c, index) for index in gt_not_in_predicted_indices]

           

    
            predicted_not_in_gts_all.extend(predicted_not_in_gt)
            gt_not_in_predicted_all.extend(gt_not_in_predicted)

             # Add all the predicted and ground truth words to calculate the micro scores
            all_predicted.extend((comment['text'].split(" ")[index]) for index in predicted_set)
            all_gt.extend((comment['text'].split(" ")[index]) for index in gt_set)

print(f"Average macro precision: {sum(precisions) / len(precisions):.2f}")
print(f"Average macro recall: {sum(recalls) / len(recalls):.2f}")

print(f"Average micro precision: {calculate_scores(all_gt, all_predicted)[0]:.2f}")
print(f"Average micro recall: {calculate_scores(all_gt, all_predicted)[1]:.2f}")

print("predicted not in ground truth")
for word in predicted_not_in_gts_all:
    print(word)
print("############################")
print("ground truth not in predicted")
print("############################")
for word in gt_not_in_predicted_all:
    print(word)
