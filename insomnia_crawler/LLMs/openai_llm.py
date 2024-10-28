from openai import OpenAI
import json
import os



client = OpenAI(api_key = os.environ.get("OPENAI_API_KEY"))


forums = os.listdir("forums_info/forums_sampled_combined")
print(forums)

model="gpt-4o-mini"

for forum in forums:
    with open(f"forums_info/forums_sampled_combined/{forum}") as f:
        forum_data = json.load(f)

    transliterated_data = []
    temperature = 0.0

    # Iterate over the posts
    for post in forum_data:
        # Perform the request
        completion = client.chat.completions.create(
        temperature=temperature,
        model=model,
        messages=[
                {"role": "system", "content": """
                You are an expert at transliterating Greeklish into Greek. Transliterate the user's input from Greeklish into Greek, while following these rules:
                - Make sure you output the transliterated text only
                - Do not correct any mistakes of the user and do not change the spacing of the words
                - If a word is not in greek, you can leave it as it is
                - Do not translate english words into greek, leave them as is"""},
                {
                    "role": "user",
                    "content": post["text"]
                }
            ]
        )
        

        # Add the transliterated data to the list
        transliterated_data.append({
            "greeklish": post["text"],
            "greek": completion.choices[0].message.content,
            "gt_indices": post["gt_indices"]
        })
        print(completion.choices[0].message.content)

    folder_path = f"LLMs/LLM_data/{model}_{temperature}_data_combined"
    # Make the dir {model}_data if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    print(f"{folder_path}{forum}")
    # Save the transliterated data
    with open(f"{folder_path}/{forum}", "w") as f:
        json.dump(transliterated_data, f, ensure_ascii=False, indent=4)



