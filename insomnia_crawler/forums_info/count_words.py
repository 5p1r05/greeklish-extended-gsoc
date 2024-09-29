import os
import json
import numpy as np

forums = os.listdir("forums_sampled")

counts = []
for forum in forums:
	with open(f"forums_sampled/{forum}", "r") as f:
		data = json.load(f)
	for post in data:
		counts.append(len(post['text'].split(" ")))

print(counts)
print(np.mean(counts))
