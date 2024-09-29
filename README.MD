# Overview

This Repository contains work done during the duration of the Google Summer of Code 2024, in collaboration with [Open Technologies Alliance - GFOSS](https://summerofcode.withgoogle.com/programs/2023/organizations/open-technologies-alliance-gfoss), [AUEB&#39;s NLP Group](http://nlp.cs.aueb.gr/), and helvia.ai

The goal of this project is to develop and evaluate a model that can convert Greeklish text (Greek written using the Latin alphabet) into Greek text (using the Greek alphabet). The model should also be able to handle inputs that contain a mix of Greeklish and English words, ensuring that the English words remain unchanged in the output.

The repository is consists of three parts:

### Insomnia Crawler

This pipeline crawls the forum threads on [insomnia.gr](insomnia.gr), a site with discussions dating back to the 2000s when Greeklish was more commonly used. The script scans each thread on the site, identifies Greeklish text, and downloads it. The forum texts often contain a mix of Greeklish and English words. The script identifies the English words and records their positions within the text. These annotations can then be used to evaluate a model's performance in ensuring that English words remain unchanged and correctly positioned in the transliterated text.

### Mixed Greeklish Training

This pipeline's objective is to train a ByT5 model ([https://huggingface.co/docs/transformers/en/model_doc/byt5]()) to translate Greeklish into Greek,while keeping the English words of the input unchanged in the output. The training process follows the approach outlined in the paper [[1]](https://aclanthology.org/2024.lrec-main.1330/), with some modifications to enable the model to effectively handle mixed text input. In the beginning of each epoch, the program randomly selectes a subset of the input and target words and substitutes them with their English translation. This approach helps the model learn that when it encounters an English word, it should leave it unchanged rather than transliterating it.

### Mixed Greeklish Evaluation

This pipeline consists of a benchmark to evaluate a model's ability to skip English words when transliterating from Greeklish into Greek. It utilizes texts containing a mix of Greeklish and English, along with annotations indicating the locations of the English words. Essentially, it uses the model to perform inference on the data and calculates:

- The CER and WER scores of the whole predicted and ground truth text.
- the CER and WER scores of the Greek parts of the predicted and ground truth texts.
- The CER and WER scores of the English parts of the predicted and ground trith texts.
- 

This is done to distinguish the model's ability of generating correct transliterations from its ability to keep the English text untransliterated.
** Note: ** As of now, the benchmark uses artificial data, but it will be extended to use real-world data from [insomnia.gr](insomnia.gr)

# Details

### Insomnia Crawler

As the Insomnia crawler scans through the forum posts, it takes each one and checks whether the majority of the letters are Greek or English. If they are Greek, it assumes that the text is in greek and skips the post, otherwise, it saves the post as it is probably written in English. This is the first preprocess step that is performed online, to save up space.

However, the texts need to be further preprocessed to remove noise, make sure that they are in Greeklish and producing annotations. This is done using the data_preprocessing module. This module performs the following steps:

- It uses Regular Expressions to remove any html tags and urls
- It uses the [facebook/fasttext-language-identification](https://huggingface.co/facebook/fasttext-language-identification) model to determine whether or not each post is written in the English language. If the post is not written in Εnglish, we assume that it is written in Greeklish. However, the text could be written in another language, but we consider it an edge case.
- It uses an English dictionary and scans through the Greeklish texts to locate the English words. Their locations are then added to the json file containing the text.

The data crawled from insomnia.gr are accompanied by the dateime that they were posted, as well as thee topic of the forum they originate.

### Mixed Greeklish Training

The training data were generated using the artificial data generation process described in [1]. This process begins with the ground truth Greek text, which is then transliterated into Greeklish following a set of fixed rules. Additionally, to help the model learn to ignore English words during transliteration, the pipeline translates every Greek word into English using the argostranslate library. As a result, the data used for training the model consists of the original Greek text, the corresponding Greeklish text, and the translated English text.

### Mixed Greeklish Evaluation

# Usage

#### Insomnia Crawler

To use the insomnia crawler run.

```bash
python3 -m insomnia_crawler.crawler
```

This will start the crawler and it will save the crawled data in the *raw_data/* directory.

To run the preprocessing pipeline, run

```bash
python3 -m insomnia_crawler.data_preprocessing --source source_folder/ --destination destination_folder/ --mode mode --english_words_path path/to/english/words/
```

modes:

- fix_encoding: convert from ascii to unicode
- clean_text: perform the preprocessing steps described above
- locate_english: use the provided English dictionary to locate the English words and annotate the data with their positions

#### Mixed Greeklish Training

  To generate the training data run

```bash
python3 mixed_greeklish_training.generate_dataset.create_mixed_texts
```

This script processes the *greek_europarl_training_100k.txt* file, located in the *mixed_greeklish_training/generate_dataset/data/* folder, which contains 100,000 sentences from the English Europarl dataset. The script performs the necessary steps to generate the English translation and Greeklish transliteration of these sentences. The results are then saved in a single JSON file within the same directory.

  To initiate the training of the ByT5 model for the mixed task, make sure that the training and evaluation data are in the directory *mixed_greeklish_training/generate_dataset/data* and then run

```bash
python3 mixed_greeklish_training.ByT5_mixed
```

The weights of the final model will be outputted into the *results/* folder

# References

[1] Toumazatos, A., Pavlopoulos, J., Androutsopoulos, I., & Vassos, S. (2024). Still All Greeklish to Me: Greeklish to Greek Transliteration. In *Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)* (pp. 15309–15319). ELRA and ICCL.

[2] [https://github.com/nlpaueb/greeklish](https://github.com/nlpaueb/greeklish) (The Github Repository of the above paper)
