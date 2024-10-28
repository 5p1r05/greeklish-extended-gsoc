import os
import json

folder_path = '/home/sp1r05/Documents/gsoc/greeklish_extended/insomnia_crawler/LLMs/LLM_data/Llama_data'

for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)