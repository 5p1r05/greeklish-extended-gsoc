import os
import json
import random
import generate_dataset.dataset_maker as dataset_maker

import argostranslate.package
import argostranslate.translate



def generate_evaluation_data(greek_sentences, substitution_percentage):
    """
        Create the mixed texts and the greeklish texts for the evaluation dataset on the mixed language task
    """
    data = []
    # data['greek'] = greek_sentences
    mixed_sentences = []
    gt_indices = []
    

    words = 0
    skips = 0

    # Iterate over the sentences and randomly substitute words
    for sentence in greek_sentences:
        # keep track of the indices of the english words
        english_words_indices = []

        greek_words = sentence.split(" ")

        mixed_words = greek_words.copy()
        for i, word in enumerate(greek_words):
            words += 1

            if random.random() < substitution_percentage:
                translation = argostranslate.translate.translate(word, 'el', 'en')
                
                # Check if the translation is a single word, and if not, skip
                if(len(translation.split(" ")) == 1):
                    mixed_words[i] = translation
                    english_words_indices.append(i)
                    # print(f"{word}:{translation}")
                    
                else:
                    skips += 1
                    continue
        
        mixed_sentence = " ".join(mixed_words)

        item = {
            'greek': sentence,
            'mixed': mixed_sentence,
            'greeklish' : dataset_maker.convert_to_greeklish([mixed_sentence])[0],
            'gt_indices': english_words_indices

        }

        data.append(item)

    # find the percentage of skips in the words
    print(f"Skips: {skips} out of {words} words, {skips/words*100}%")
    return data


if __name__ == "__main__":
    random.seed(42)
    substitution_percentage = 0.15
    dataset_size = 300

    greek_text_path = "generate_dataset/data/greek_europarl_training_100k.txt"

    # select a random subset of 300 sentences
    with open(greek_text_path, "r") as f:
        greek_text = f.readlines()

    num_sentences = len(greek_text)
    greek_sentences = random.sample(greek_text, dataset_size)

    greek_sentences = [sentence.replace('\n', '') for sentence in greek_sentences]

    data = generate_evaluation_data(greek_sentences, substitution_percentage)
    
    # Save the data
    with open(f"evaluation_data/mixed_evaluation_data_{dataset_size}_sentences.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)




