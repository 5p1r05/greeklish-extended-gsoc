import json


def find_idx(text):
    text = text.split(" ")

    for i, word in enumerate(text):
        print(word, i)


# file = "forums_info/forums_sampled/Ψυχαγωγία_sample.json"

# with open(file, "r") as f:
#     data = json.load(f)

# find_idx(data[15]["text"])

find_idx("kai ektos ayto kalhtrero einia na kaneis esy oti khniseis thes me thn karta sou para to na piarnei prwtovoulia to site kathe fora pou kerdizeis")