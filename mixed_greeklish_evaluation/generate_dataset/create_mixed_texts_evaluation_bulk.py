import os
import json
import random
import generate_dataset.dataset_maker as dataset_maker

import argostranslate.package
import argostranslate.translate

from generate_dataset.create_mixed_texts_evaluation import generate_evaluation_data


if __name__ == "__main__":

    random.seed(42)
    substitution_percentages = [0, 0.05, 0.1, 0.15, 0.2]
    dataset_size = 300

    greek_text_path = "generate_dataset/data/greek_europarl_training_100k.txt"

    # select a random subset of 300 sentences
    with open(greek_text_path, "r") as f:
        greek_text = f.readlines()

    num_sentences = len(greek_text)
    greek_sentences = random.sample(greek_text, dataset_size)

    greek_sentences = [sentence.replace('\n', '') for sentence in greek_sentences]


    for percentage in substitution_percentages:
        data = generate_evaluation_data(greek_sentences, percentage)
        
        # Save the data
        with open(f"evaluation_data/mixed_evaluation_data_{dataset_size}_sentences_{percentage}_percentage.json", "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # data = generate_evaluation_data(greek_sentences, substitution_percentage)
    
    # # Save the data
    # with open(f"evaluation_data/mixed_evaluation_data_{dataset_size}_sentences.json", "w") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)


