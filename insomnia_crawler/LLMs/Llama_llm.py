from groq import Groq
import os
import json

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

forums = os.listdir("forums_info/forums_sampled_combined")
print(forums)

# model="llama-3.1-70b-versatile"
# model = "llama-3.1-8b-instant"
model = "llama-3.2-1b-preview"
# model = "llama3-70b-8192"
# Iterate over the forums
for forum in forums:
    with open(f"forums_info/forums_sampled_combined/{forum}") as f:
        forum_data = json.load(f)

    transliterated_data = []
    temperature = 0.0

    # Iterate over the posts
    for post in forum_data:
        # Perform the request
        chat_completion = client.chat.completions.create(
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
            ],
            # model = "llama-3.1-8b-instant"
            model=model,
            temperature=temperature,
        )
        print(chat_completion.choices[0].message.content)

        # Add the transliterated data to the list
        transliterated_data.append({
            "greeklish": post["text"],
            "greek": chat_completion.choices[0].message.content,
            "gt_indices": post["gt_indices"]
        })

    folder_path = f"LLMs/LLM_data/{model}_{temperature}_data_combined"
    # Make the dir {model}_data if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    print(f"{folder_path}{forum}")
    # Save the transliterated data
    with open(f"{folder_path}/{forum}", "w") as f:
        json.dump(transliterated_data, f, ensure_ascii=False, indent=4)



print(chat_completion.choices[0].message.content)

# chat_completion = client.chat.completions.create(
#     messages=[
#         {"role": "system", "content": "Transliterate the user's message from greeklish into greek. make sure you output the transliterated text only without anything else. You must follow these rules"},
#         {
#             "role": "user",
#             "content": "Pare epwnymo trofodotiko, estw kai 300w, mporei na se swsei apo polla!! 8a sou proteina na pareis to ANTEC SMARTPOWER 350watt! Exei liges meres pou to phra kai pistevw oti htan mia poly kalh epilogh! Mono 80 eurw, 3 xronia egiisi ta xarakthristika tou ksepernane xalara ena noname 450 watt!!!! Gia tou logou to alithes sou lew oti exei 3,3v kai 5v combined 230watt(oi grammes autes dhl oi 3,3 kai h 5 einai oi shmantikoteres pou prepei na koitas se ena trofodotiko, eidika se platformes Athlon) se anti8esh me kapoio noname 350 watt pou 8a dwsei to poly 180-190 watt! Exei PFC(power factor correction) kati pou dyskola 8a vreis se noname PSU kai systhma diakophs leitourgias se periptwsh yperfwrtwshs!! Gia thn psixi tou yparxoun 2 anemisthres enas 80mm kai enas 92mm pou rithmizoun tis strofes analoga me thn 8ermokrasia! Sto proteinw an psaxneis gia ena poly kalo trofodotiko sta 350watt, pou den kaigetai eukola!! An h tseph sou antexei vevea pare to TRUEPOWER 380 watt, oti kalytero, symfwna me metrhseis vgazei alithina 471 watt!!!! tsekare autes tis dieu8ynseis: , kai Filika"
#         }
#     ],
#     model="llama3-70b-8192",
# )

