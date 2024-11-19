import os
import json
import time
import tqdm
import allgreek2me_master.greeklish as greeklish



# inference on the synthetic data
path = '/home/sp1r05/Documents/gsoc/greeklish_extended/mixed_greeklish_evaluation/evaluation_data/mixed_evaluation_data_300_sentences.json'
base_path = '/home/sp1r05/Documents/gsoc/greeklish_extended/mixed_greeklish_evaluation/evaluation_data/'

g2g = greeklish.GreeklishConverter()

data_paths = os.listdir(base_path)

# Get the avaliable substitution percentages from the names of the files
# percentages = [float(name.split('_')[5]) for name in data_paths]


# with open(base_path, 'r') as f:
#     data = json.load(f)

# Iterate over the sentences and perform inference

model = "allgreek2me"

# Iterate over the different files with varying degrees of substitution
for data_path in data_paths:
    percentage = float(data_path.split('_')[5])
    
    print(percentage)

    with open(os.path.join(base_path, data_path), 'r') as f:
        sentences = json.load(f)

    transliterated_data = []

    # Iterate over the sentences
    for i, sentence in tqdm.tqdm(enumerate(sentences)):
        transliterated_text = g2g.convert(sentence['greeklish'])
        
        transliterated_data.append({
            "greeklish": sentence['greeklish'],
            "greek": sentence['greek'],
            "mixed": sentence['mixed'],
            'greek_predicted': transliterated_text,
            'gt_indices': sentence['gt_indices']
        })

        if not os.path.exists(f"robustness_test/{model}"):
            os.makedirs(f"robustness_test/{model}")

        destination_path = f"LLMs/robustness_test/{model}/{percentage}_synthetic_data_{len(sentences)}2.json"

        
        # Save the transliterated data
        with open(destination_path, "w") as f:
            json.dump(transliterated_data, f, ensure_ascii=False, indent=4)

    