import os
import json
import random
import argostranslate.package
import argostranslate.translate

import dataset_maker
import tqdm


def mix_texts(greek_text_path, english_text_path, num_sentences, substitution_probability):
    """
    Mixes two aligned texts, greek and english, by randomly substituting sentences from the english text to the greek text.

    Args:
        greek_text_path (str): Path to the greek text file.
        english_text_path (str): Path to the english text file.
        num_sentences (int): Number of sentences.
        substitution_probability (float): Probability of substituting an english sentence to the greek text.

    Returns:
        dict: A dictionary containing the mixed text and the indices of the english sentences that were substituted.
    """

    greek_english_data = {}

    # Read the files
    with open(greek_text_path, "r") as f:
        greek_text = f.readlines()

    with open(english_text_path, "r") as f: 
        english_text = f.readlines()

    greek_english_data['text'] = []
    greek_english_data['masked_indices'] = []


    # Iterate over the sentences and randomly substitute 
    # greek sentences with the corresponding english ones
    for i in range(num_sentences):
        if(random.random() < substitution_probability):
            greek_english_data['text'].append(english_text[i])
            greek_english_data['masked_indices'].append(i)
        else:
            greek_english_data['text'].append(greek_text[i])

    return greek_english_data

def substitute_words(greek_text_path, num_sentences):
    """
    Substitutes words in a greek text with random english words.

    Args:
        greek_text_path (str): Path to the greek text file.
        substitution_probability (float): Probability of substituting a word.

    Returns
    """
    with open(greek_text_path, "r") as f:
        greek_text = f.readlines()
    
    if(num_sentences == 'all'):
        num_sentences = len(greek_text)

    # Load the translator
    # translator = googletrans.Translator()
    greek_english_data = {}
    greek_english_data['english'] = []
    

    for i in tqdm.tqdm(range(num_sentences)):
        words = greek_text[i].split()
        for j, word in enumerate(words):

            translation = argostranslate.translate.translate(word, 'el', 'en')

            words[j] = translation.split(' ')[0]

        greek_english_data['english'].append(" ".join(words))
    
    greek_english_data['greek'] = greek_text[:num_sentences]
        

    return greek_english_data



if __name__ == "__main__":
    greek_text_path = "/home/sp1r05/Documents/gsoc/greeklish/data/artificial/greek/greek_europarl_training_100k.txt"
    # english_text_path = "mixed_languages/data/europarl-v7.el-en.en"

    num_sentences = 10
    random.seed(1234)

    # Substitute words
    greek_english_data = substitute_words(greek_text_path, num_sentences)

    # Create the greeklish version of the mixed text
    greek_english_data['greeklish'] = dataset_maker.convert_to_greeklish(greek_english_data['greek'])

    with open(f"mixed_languages/data/greeklish_mixed_europarl_words_{num_sentences}.json", "w", encoding ='utf8') as f:
        json.dump(greek_english_data, f, ensure_ascii=False)