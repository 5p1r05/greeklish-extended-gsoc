# -*- coding: utf-8 -*-
# ===================================  MT5  ===================================
import math
import random
import torch
from transformers import T5ForConditionalGeneration, AutoTokenizer
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader
import time
import json


# Helper class for splitting data into batches
class GreeklishDataset(Dataset):
    def __init__(self, text_data, tokenizer=None, substitution_probability=0.2):

        self.tokenizer = tokenizer
        self.substitution_probability = substitution_probability
        
        self.english_text = text_data['english']
        self.greek_text = text_data['greek']
        self.greeklish_text = text_data['greeklish']

        self.mixed_greek_text = self.greek_text.copy()
        self.mixed_greeklish_text = self.greeklish_text.copy()

        self.source_encodings = None
        self.target_encodings = None

        self.create_dataset()


    def __getitem__(self, idx):
        # don't forget we need both the idxs and the attention mask from the source
        source = {key: torch.tensor(val[idx]) for key, val in self.source_encodings.items()}
        target = torch.tensor(self.target_encodings[idx])
        return source, target
    

    def __len__(self):
        return len(self.greeklish_text)

    def create_dataset(self):
        """
            Change the greeklish and greek texts by 
            substituting random words with their corresponding english ones.
        """
    
   

        english_text = [sent.split(" ") for sent in self.english_text]
        self.mixed_greek_text = [sent.split(" ") for sent in self.greek_text]
        self.mixed_greeklish_text = [sent.split(" ") for sent in self.greeklish_text]

        # Substitute random greek words with their corresponding english ones
        for i in range(len(self.mixed_greeklish_text)):
            for j in range(len(self.mixed_greeklish_text[i])):
                if random.random() < self.substitution_probability:
                    # print(f"{self.mixed_greeklish_text[i][j]}->{english_text[i][j]}")
                    self.mixed_greeklish_text[i][j] = english_text[i][j]
                    self.mixed_greek_text[i][j] = english_text[i][j]
        
        self.mixed_greek_text = [" ".join(sent) for sent in self.mixed_greek_text]
        self.mixed_greeklish_text = [" ".join(sent) for sent in self.mixed_greeklish_text]
        
        # print("greek")
        # print(self.mixed_greek_text)
        # print("greeklish")
        # print(self.mixed_greeklish_text)
        # print("english")
        # print(self.english_text)
        

        self.source_encodings = self.tokenizer(self.mixed_greeklish_text, padding=True)
        self.target_encodings = self.tokenizer(self.mixed_greek_text, padding=True)['input_ids']





# import data
with open("mixed_languages/data/greeklish_mixed_europarl_words_10.json", "r", encoding="utf-8") as file:
    data = json.load(file)


version = "small"

# choose training/val datasets
# random.seed(12345)
# random.shuffle(train_x)
# random.seed(12345)
# random.shuffle(train_y)

data_size = len(data['greeklish'])

train_data = {key: val[: math.ceil(data_size * 0.8)] for key, val in data.items()}
val_data = {key: val[math.ceil(data_size * 0.8): data_size] for key, val in data.items()}

# # 80/20 split

# # ================ Fine-Tuning =================
model = T5ForConditionalGeneration.from_pretrained("google/byt5-{}".format(version))
tokenizer = AutoTokenizer.from_pretrained("google/byt5-{}".format(version))

# test

# Padded to the length of the longest sentence


train_dataset = GreeklishDataset(train_data, tokenizer, substitution_probability=0.2)
val_dataset = GreeklishDataset(val_data, tokenizer, substitution_probability=0.2)

train_dataset.create_dataset()
val_dataset.create_dataset()


# Training loop
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

batch_size = 1
learning_rate = 5e-5
epochs = 3
accumulation_steps = 9

model.to(device)
model.train()

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=True)

# Optimizer & lr decay
optim = AdamW(model.parameters(), lr=learning_rate)
scheduler = torch.optim.lr_scheduler.StepLR(optim, step_size=11, gamma=0.5)  # decrease the lr to half every 11 epochs

training_losses = []
validation_losses = []

model.zero_grad(set_to_none=True)

print("Training started")
best_loss = None
for epoch in range(1, epochs + 1):
    print("\nEpoch {}/{}".format(epoch, epochs))
    train_loss = 0
    for i, (sources, targets) in enumerate(train_loader):

        print("source")
        print(len(sources['input_ids'][0]))
        print("target")
        print(len(targets[0]))


        # Print progress of epoch
        print("\r[{}{}] Batch {}/{}".format(math.ceil((i + 1) / len(train_loader) * 40) * "=",
                                            (40 - math.ceil((i + 1) / len(train_loader) * 40)) * " ", i + 1,
                                            len(train_loader)), end="")
        # optim.zero_grad()
        # Convert ids to text

        # Unpack the batch & push to device
        input_ids = sources['input_ids'].to(device)
        attention_mask = sources['attention_mask'].to(device)
        labels = targets.to(device)

        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)

        loss = outputs[0]
        train_loss += loss  # For loss loging at the end of the epoch

        # Grad accumulation
        if (i / accumulation_steps == len(train_loader) / accumulation_steps) and (
                len(train_loader) % accumulation_steps != 0):
            loss = loss / (len(train_loader) % accumulation_steps)  # The last batches may not be enough for a full accumulation step
        else:
            loss = loss / accumulation_steps

        loss.backward()

        # if (i+1) % accumulation_steps == 0:
        if (i + 1) % accumulation_steps == 0 or i == len(train_loader) - 1:  # If the finally batches can't if a full accumulation step
            optim.step()
            model.zero_grad(set_to_none=True)

    # Validation
    model.zero_grad()
    with torch.no_grad():
        model.eval()
        val_loss = 0
        for i, (sources, targets) in enumerate(val_loader):
            input_ids = sources['input_ids'].to(device)
            attention_mask = sources['attention_mask'].to(device)
            labels = targets.to(device)

            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)

            loss = outputs[0]
            val_loss += loss

    # Calculate losses for the epoch
    epoch_train_loss = train_loss / len(train_loader)
    epoch_val_loss = val_loss / len(val_loader)

    training_losses.append(epoch_train_loss.item())
    validation_losses.append(epoch_val_loss.item())

    print(" Loss: (train){} (val){}".format(epoch_train_loss, epoch_val_loss))
    print("train: {}".format(training_losses))
    print("val: {}".format(validation_losses))

    # Save the models (if val loss has improved)
    # if not best_loss:
    #     best_loss = epoch_val_loss

    #     tokenizer.save_pretrained(save_path + "ByT5_{}_{}_samples".format(version, data_size))
    #     model.save_pretrained(save_path + "ByT5_{}_{}_samples".format(version, data_size))
    # elif (best_loss > epoch_val_loss):
    #     best_loss = epoch_val_loss

    #     tokenizer.save_pretrained(save_path + "ByT5_{}_{}_samples".format(version, data_size))
    #     model.save_pretrained(save_path + "ByT5_{}_{}_samples".format(version, data_size))

    scheduler.step()

    train_dataset.create_dataset()

# =============== Training Done ===============
# Translate a sentence
with torch.no_grad():
    model.eval()
    sample = "Ena paradeigma sta ellinika."
    print("\n{}".format(sample))
    encoded_sample = tokenizer(sample, return_tensors="pt").input_ids.to(device)
    output = model.generate(encoded_sample, max_length=10000)
    print(tokenizer.decode(output[0]))


    