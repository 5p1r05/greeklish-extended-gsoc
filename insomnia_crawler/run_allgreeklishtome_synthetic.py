import json
import os
import allgreek2me_master.greeklish as greeklish


# inference on the synthetic data
path = '/home/sp1r05/Documents/gsoc/greeklish_extended/mixed_greeklish_evaluation/evaluation_data/mixed_evaluation_data_300_sentences.json'
# model = "llama-3.1-70b-versatile"
model = "allgreek2me"

g2g = greeklish.GreeklishConverter()


with open(path, 'r') as f:
    data = json.load(f)

# Iterate over the sentences and perform inference

transliterated_data = []

for i, sentence in enumerate(data):
    transliterated_text = greek_text = g2g.convert(sentence['greeklish'])
    
    transliterated_data.append({
        "greeklish": sentence['greeklish'],
        "greek": sentence['greek'],
        "mixed": sentence['mixed'],
        'greek_predicted': transliterated_text,
        'gt_indices': sentence['gt_indices']
    })
    
    

folder_path = f"LLMs/LLM_data/{model}_synthetic_data"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

print(f"{folder_path}/synthetic_data_{len(data)}.json")

    # Save the transliterated data
with open(f"{folder_path}/synthetic_data_{len(data)}.json", "w") as f:
    json.dump(transliterated_data, f, ensure_ascii=False, indent=4)
    
    
    