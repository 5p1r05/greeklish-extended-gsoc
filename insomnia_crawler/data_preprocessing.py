import json
import os
import argparse
import re

import fasttext
from huggingface_hub import hf_hub_download
from spellchecker import SpellChecker

import nltk
from nltk.corpus import stopwords
import tqdm

# nltk.download('stopwords')

def dominant_language(text):
    """
    Checks whether the majority of the letters in the input text are in the greek or the latin script
    In this specific scenario, we need to be more strict on the usage of greek letters, since we are looking for greeklish texts,
    so the threshold is set to 20%  

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
    
    # Check if the number of letters in greek is more than 20% of the total number of letters
    if greek_count > all_count * 0.2:
        return "greek"
    else:
        return "latin"
    
def binary_search(arr, low, high, x):
        
        """
        This function performs a binary search on the input array to find the index of the input element

        Args:
            arr (list): The input array
            low (int): The lower bound of the search
            high (int): The upper bound of the search
            x (str): The element to search for
        """
        
 
        # Check base case
        if high >= low:
    
            mid = (high + low) // 2
            # If element is present at the middle itself
            # print(mid)
            if arr[mid] == x:
                
                return mid
    
            # If element is smaller than mid, then it can only
            # be present in left subarray
            elif arr[mid] > x:
                return binary_search(arr, low, mid - 1, x)
    
            # Else the element can only be present in right subarray
            else:
                return binary_search(arr, mid + 1, high, x)
    
        else:
            # Element is not present in the array
            return -1
        
def add_spaces_after_punctuation(text):
    # Regular expression to find punctuation marks followed directly by letters
    corrected_text = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', text)
    return corrected_text

class DataPreprocessing:

    """
    Used to perform the preprocessing steps on the crawled data from insomnia.gt

    Args:
        source (str): The folder containing the data
        destination (str): The folder to save the preprocessed data
        mode (str): The preprocessing step to apply

    Atrributes:
        source (str): The folder containing the data
        destination (str): The folder to save the preprocessed data
        model (fasttext.FastText._FastText): The fasttext model to detect the language of the text
    
    """

    def __init__(self, source, destination, mode, exclude_words_path=None):
        self.source = source
        self.destination = destination

        if(mode == 'clean_text'):
            model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
            self.model = fasttext.load_model(model_path)
        
        elif(mode == 'locate_english'):
            with open(exclude_words_path, 'r', encoding='utf-8') as f:
                self.exclude_words = json.load(f)


        self.stopwords = set(stopwords.words('english'))
        
    


    def fix_encoding(args):
        """
        Converts The ascii coded text into UTF-8 coded text

        Args:
            args (argparse.Namespace): The arguments passed to the script
        
        """
        source_files = os.listdir(args.source)

        for file in source_files:
            with open(os.path.join(args.source, file), 'r', encoding='utf-8') as f:
                data = json.load(f)

            with open(os.path.join(args.destination, file), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        
        print("Encoding fixed")


    def clean_data(self):

        """
        This function performs the following actions:
        - Removes the urls
        - Removes the html tags
        - Removes the new lines
        - Removes the texts that are in greek
        - Removes the texts that are shorter than 4 words
        - Removes the texts that are in english
        - Saves the cleaned data in the destination folder

        The goal of this function is to obtain the cleaned greeklish texts and discard the rest.
        
        """
        source_files = os.listdir(self.source)

        for file in source_files:
            print(file)
            with open(os.path.join(self.source, file), 'r', encoding='utf-8') as f:
                data = json.load(f)

            data_cleaned = []
            

            for text_data in data:
                text_data_cleaned = {}

                text = text_data['text']

                # Remove urls
                text = re.sub(r"https?://(?:www\.)?\S+|www\.\S+", "", text)
                
                # Remove the html tags
                text = re.sub(r"<[^>]+>", "", text)

                # Remove the new lines
                text = text.strip().replace('\n', ' ')

                # Remove extra spaces
                text = " ".join(text.split())

                # Add spaces after punctuation
                text = add_spaces_after_punctuation(text)

                # If the rest of the text is in greek, then skip this text
                lang = dominant_language(text)
                if(lang == 'greek'):
                    continue
                
                word_count = len(text.split())

                # If the text is shorter than 4 words, skip this text
                if(word_count < 4):
                    continue

                # Check if the text is in english or in greek
                # If it is in english, skip this text
                
                pred = self.model.predict(text, k=1)
                # print(pred)
                if(pred[0][0] == '__label__eng_Latn'):
                    continue

                text_data_cleaned['text'] = text
                text_data_cleaned['time'] = text_data['time']

                data_cleaned.append(text_data_cleaned)
            

            with open(os.path.join(self.destination, file), 'w', encoding='utf-8') as f:
                json.dump(data_cleaned, f, ensure_ascii=False)


    def locate_english(self):
        """
        This function locates the english words in the text and saves the indices of the english words in the text
        """
        source_files = os.listdir(self.source)

        # Create a spellchecker object to check if the word are english words
        spellChecker = SpellChecker()

        # English words across all the files
        english_words_all = {}



        # Iterate over the source files 
        for file in tqdm.tqdm(source_files):

            with open(os.path.join(self.source, file), 'r', encoding='utf-8') as f:
                file_data = json.load(f)

            file_data_annotated = []

            # English for this specific file
            english_words = {}
            
            # Iterate over the text data
            for text_data in file_data:
                text_data_annotated = {}

                english_words_indices = []

                

                # spit the text into words
                words = text_data['text'].split(" ")

                # Detect the text's words
                for i, word in enumerate(words):

                    # Remove the characters in the string that are not letters 
                    word = " ".join(re.findall("[a-zA-Z]+", word))

                    # Convert the word to lowercase
                    word = word.lower()

                    # Check if the word is more than one letter, if the word is not a stopword, if the word is in the spellchecker and if the word is not in the exclude words
                    if(len(word) > 1 and word not in self.stopwords and word in spellChecker and word not in self.exclude_words):
                        english_words_indices.append(i)

                        # Add the word to the english words across all the files
                        if(word not in english_words_all):
                            english_words_all[word] = 1
                        else:  
                            english_words_all[word] += 1

                        # Add the word to the english words of this file
                        if(word not in english_words):
                            english_words[word] = 1
                        else:
                            english_words[word] += 1


                text_data_annotated['text'] = text_data['text']
                text_data_annotated['time'] = text_data['time']
                text_data_annotated['english_indices'] = english_words_indices
            
                file_data_annotated.append(text_data_annotated)

            with open(os.path.join(self.destination, file), 'w', encoding='utf-8') as f:
                json.dump(file_data_annotated, f, ensure_ascii=False)

            
            with open(os.path.join(os.path.join(os.path.dirname(self.destination), "forums_info/english_words"), f"english_words_{file}"), 'w', encoding='utf-8') as f:
                json.dump(english_words, f, ensure_ascii=False)

            
        with open(os.path.join(os.path.join(os.path.dirname(self.destination), "forums_info/english_words"), "english_words.json"), 'w', encoding='utf-8') as f:
            json.dump(english_words_all, f, ensure_ascii=False)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Preprocess the data")
    parser.add_argument("--source", type=str, help="The folder containing the data")
    parser.add_argument("--destination", type=str, help="The folder to save the preprocessed data")
    parser.add_argument("--mode", type=str, help="the preprocessing step to apply", choices=['fix_encoding', 'clean_text', 'locate_english'])
    parser.add_argument("--exclude_words", type=str, help="The path to the file containing the greek words to exclude", default="insomnia_crawler/forums_info/greek_english_overlap.json")
    # parser.add_argument("--english_words_path", type=str, help="The path to the file containing the english words", default="words_10000.txt")

    args = parser.parse_args()

    data_preprocessor = DataPreprocessing(args.source, args.destination, args.mode, args.exclude_words)#, english_words_path= args.english_words_path)




    if(args.mode == 'fix_encoding'):
        data_preprocessor.fix_encoding()
    elif(args.mode == 'clean_text'):
        data_preprocessor.clean_data()
    elif(args.mode == 'locate_english'):
        data_preprocessor.locate_english()
    else:
        print("unsupproted mode")
