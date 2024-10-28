import allgreek2me_master.greeklish as greeklish
import os 
import json


forums = os.listdir("forums_info/forums_sampled_combined")
g2g = greeklish.GreeklishConverter()

for forum in forums:
    with open(f"forums_info/forums_sampled_combined/{forum}") as f:
        forum_data = json.load(f)

    transliterated_data = []

    # Iterate over the posts
    for post in forum_data:

        # Convert the text
        predicted_text = g2g.convert(post['text'])
        

        # Add the transliterated data to the list
        transliterated_data.append({
            "greeklish": post["text"],
            "greek": predicted_text,
            "gt_indices": post["gt_indices"]
        })
        print(predicted_text)

    folder_path = "LLMs/LLM_data/allgreek2me_data_combined/"
    # Make the dir {model}_data if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    print(f"{folder_path}{forum}")
    # Save the transliterated data
    with open(f"{folder_path}/{forum}", "w") as f:
        json.dump(transliterated_data, f, ensure_ascii=False, indent=4)