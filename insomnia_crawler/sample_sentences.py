import os
import json
import random

forums = os.listdir('forums_annotated')

random.seed(36)

for forum in forums:
    with open(f'forums_annotated/{forum}', 'r') as f:
        data = json.load(f)

    random_elements = random.sample(data, 17)
    
    forum_name = forum.split('.')[0]

    with open(f'forums_info/forums_sampled/{forum_name}_sample2.json', 'w') as f:
        json.dump(random_elements, f, indent=4, ensure_ascii=False)