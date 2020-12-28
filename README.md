![GLUE](assets/img/glue_logo.png)

## About GLUE
GLUE a lightweight, Python-based collection of scripts to support you at succeeding with speech and text use-cases based on [Microsoft Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/). It not only allows you to batch-process data, rather glues together the services of your choice in one place and ensures an end-to-end view on the training and testing process.

## Modules
GLUE consists of multiple modules, which either can be executed separately or ran as a central pipeline:
- Batch-transcribe audio files to text transcripts using [Microsoft Speech to Text Service](https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/) (STT)
- Batch-synthesize text data using [Microsoft Text to Speech Service](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/) (TTS)
- Batch-evaluate reference transcriptions and recognitions

- Batch-score text strings on an existing, pre-trained [Microsoft LUIS](https://luis.ai)-model

TBD:
- Batch-translate text data using [Microsoft Translator](https://azure.microsoft.com/en-us/services/cognitive-services/translator/)

## Getting Started
This section describes how you get started with GLUE and which requirements need to be fulfilled by your working environment.

### Prerequisites
Before getting your hands on the toolkits, make sure your local computer is equipped with the following frameworks and base packages:
- [Python](https://www.python.org/downloads/windows/) (required, Version 3.8 is recommended)
- [VSCode](https://code.visualstudio.com/docs/?dv=win) (recommended), but you can also run the scripts using PowerShell, Bash etc.
- Stable connection for installing your environment and scoring the files

### Setup of Virtual Environment
1. Open a command line of your choice (PowerShell, Bash)
2. Change the directory to your preferred workspace (using `cd`)
3. Clone the repository (alternatively, download the repository as a zip-archive and unpack your file locally to the respective folder)
```
git clone https://github.com/microsoft/glue
```
4. Enter the root folder of the cloned repository
```
cd glue
```
5. Set up the virtual environment
``` 
python -m venv .venv
```
6. Activate the virtual environment
```bash
# Windows: 
.venv\Scripts\activate
# Linux: 
.venv/bin/activate
```
7. Install the requirements 
```
pip install -r requirements.txt
```
8. (optional) If you want to use Jupyter Notebooks, you can register your activated environment using the command below
```
python -m ipykernel install --user --name glue --display-name "Python (glue)"
```
After successfully installing the requirements-file, your environment is set up and you can go ahead with the next step.

### API Keys
In the root directory of the repository, you can find a file named `config.sample.ini`. This is the file where the API keys and some other essential confirguation parameters have to be set, depending on which services you would like to use. First, create a copy of `config.sample.ini` and rename it to `config.ini` in the same directory. You only need the keys for the services you use during your experiment. However, keep the structure of the `config.ini`-file as it is to avoid errors. The toolkit will just set the values as empty, but will throw an error when the keys cannot be found at all.

An instruction on how to get the keys can be found [here](GetYourKeys.md).

### Input Parameters
The following table shows and describes the available modes along with their input parameters as well as dependencies.

| __Mode__           | __Command line parameter__ | __Description__                                                         | __Dependencies__                                                                                                                                                                               |   |
|--------------------|----------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| __TTS__            | `--do_synthesize`          | Activate text-to-speech synthetization                                  | Requires csv file with `text`-column, see `--audio_files`                                                                                                                                      |   |
| __STT__            | `--do_transcribe`          | Activate speech-to-text processing                                      | Requires audio files, see `--audio_files`                                                                                                                                                      |   |
| __STT__            | `--audio_files`            | Path to folder with audio files                                         | Audio files have to be provided as WAV-file with the parameters described [here](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-custom-speech-test-and-train) |   |
| __STT-Evaluation__ | `--do_evaluate`            | Activate evaluation of transcriptions based on reference transcriptions | Requires csv-file with `text`-column and intent names                                                                                                                                          |   |
| __LUIS__           | `--do_scoring`             | Activate LUIS model scoring                                             | Requires csv-file with `intent` and `text` columns                                                                                                                                             |   |
| __STT / TTS__      | `--input`                  | Path to comma-separated text input file                                 |                                                                                                                                                                                                |   |

The requirements for the input files (`--input` and `--audio`)

## GLUE-Modules
This section describes the single components of GLUE, which can either be ran autonomously or, ideally, using the central orchestrator.

`glue.py`
- Central application orchestrator of the toolkit.
- Glues together the single modules in one place as needed.
- Reads input files and writes output files.

`stt.py`
- Batch-transcription of audio files using [Microsoft Speech to Text API](https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/).
- Allows baseline models as well as custom endpoints.
- Functionality is limited to the languages and locales listed on the [language support](hhttps://docs.microsoft.com/de-de/azure/cognitive-services/speech-service/language-support#speech-to-text) page.

`tts.py`
- Batch-synthetization of text strings using [Microsoft Text to Speech API](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/).
- Supports Speech Synthesis Markup Language (SSML) to fine-tune and customize the pronunciation, as described in the [documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/speech-synthesis-markup?tabs=python).
- Functionality is limited to the languages and fonts listed on the [language support](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support#text-to-speech) page.
- Make sure the voice of your choice is available in the respective Azure region ([see documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech#standard-and-neural-voices)).

`luis.py`
- Batch-scoring of intent-text combinations using an existing LUIS model
  -  See the following [quickstart documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-get-started-create-app) in case you need some inspiration for your first LUIS-app.
- Configureable scoring treshold, if predictions only want to be accepted given a certain confidence score returned by the API.
- Writes scoring report as comma-separated file.
- Returns classification report and confusion matrix based on [scikit-learn](https://github.com/scikit-learn/scikit-learn).

`evaluate.py`
- Evaluation of transcription results by comparing them with reference transcripts.
- Calculates metrics such as [Word Error Rate (WER)](https://en.wikipedia.org/wiki/Word_error_rate), Sentence Error Rate (SER), Word Recognition Rate (WRR).
- Implementation based on [github.com/belambert/asr-evaluation](https://github.com/belambert/asr-evaluation).
- See some hints on [how to improve your Custom Speech accuracy](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-custom-speech-evaluate-data).

`params.py`
- Collects API and configuration parameters from the command line (ArgumentParser) and the `config.ini`.

`helper.py`
- Collection of helper functions which do not have a purpose on their own, rather complementing the orchestrator and keeping the code neat and clean.

### Input File Guidelines
Depending on your use-case, you have to provide an input text file and/or audio files. In these cases, you have to pass the path to the respective input file of folder via the command line. There are some rules how the input files have to look like.

-
- Comma-separated file (If you only have an Excel sheet, you can create it using Excel: (_Save as_ -> comma-separated)
- UTF-8 encoding (to make sure it has the correct encoding, open it with a text editor such as [Notepad++](https://notepad-plus-plus.org/downloads/) -> Encoding -> Convert to UTF-8)
- Column names with the respective values dependent on the mode
- of columns _intent_ (ground-truth LUIS-intent) and _text_ (utterance of the text, max length of 500 characters)
- We recommend you to put the input file in the subfolder `input`.


You can find an example file [here](input/testset-example.txt).

### Text to Speech


### Get a Train-Test-Split
There are two approaches how to do this. You can either bring a pre-defined data set and use it as test data. If you have a big data set and want to have a split of it, first use `helper.py` to get a stratified split. Stratifiyng the data set means, that you will get a sample of 25% of the data, which is not randomly sampled. The sampling mode helps you to make sure that sufficient examples of every class are present in the test data set.

The file will then be written to the input folder of the repository with the following notation:<br>`[yyyy-mm-dd-]-stratify-test.txt`

Use this as input parameter for the `main.py`.later on.

__INFO:__ if you do not need to get a sample from the data and just take the whole one as test set, just skip this and continue with the step below!

### Scoring of LUIS Test Data Set
This section helps you to start your LUIS scoring with help of `main.py`. With the command line or IDE of your choice, navigate to the root directory of the Data Science repository. Among others, you can pass the following parameters (the others are not covered by this documentation as they are not needed):

```
--input INPUT           give the whole path to tab-delimited file
--mode MODE             mode, either score or eval
--subfolder SUBFOLDER   input folders, pass comma-separated if multiple ones
--treshold TRESHOLD     Set minimum confidence score between 0.00 and 1.00
--do_scoring            Text to speech using Microsoft Speech API
```

1. Make sure your virtual environment is activated, otherwise do by <br>`venv/Scripts/activate`
1. Put your tab-delimited scoring file into the `input` folder of the repository and make sure that it has the columns `intent` and `text`. Otherwise, the script will not find the correct values.
1. Execute the following command:<br>
`python code/main.py --input input/scoringfile.txt --do_scoring`<br>
The default treshold value for the LUIS scores is `0.82`, but you can choose a custom one by additionally passing `--treshold 0.91`, e.g.:<br>
`python code/main.py --input input/scoringfile.txt --do_scoring --treshold 0.91`<br>If you want to avoid the drop, just pass `--treshold 0`.
1. The scoring may take a while and you will receive some log information in your command line. For every utterance, you will see logs which prediction the LUIS model returned. If you only get back the message `prediction` in every row, there is something wrong with the keys and you should cancel the scoring with `ctrl + c`
1. When the scoring is finished, you will get a classification report and a confusion matrix, which provides you an overview on the model performance based on the given test data set. There will be two of them: one with the drop defined by the `--treshold` and the other one without considering the drops.
1. After finishing, you will find the output files in the `output` directory (which you find in the parent folder above the repository). In this folder, there is an `input` folder, containing the input file of the scoring round. In the case folder itself, you will find a `[date]-case.txt` file with the respective scorings, e.g. `2020-07-23-case`.

#### Output format
The script generates a case folder for every run and will have the structure below. Every file you used will be registered here as well and copies to the input folder to allow traceability.
```
- case: [yyyy-mm-dd]-case/
 | -- input/
    | -- [input file]
 | -- [yyyy-mm-dd]-[lang]-case.txt
 | -- transcriptions.txt (can be ignored in this context)
```

The following table shows the structure of the scoring file and gives you an example how predictions are handled, also when the confidence score is low.
| intent | text | prediction | score | drop |
| --- | --- | --- | --- | --- |
| Intent name based on reference Excel file | Raw text string | Predicted intent by LUIS app | Certainty score of LUIS model, between 0 and 1 | Predicted intent by LUIS app, _None_-intent in case of dropped value (when below the confidence score e.g. of 0.82) |
| Book_Flight | I would like to book a flight to Frankfurt. |	Book_Flight |	0.9450068 | Book_Flight |
| Flight_Change | Please rebook my flight to Singapore, please | Change_Flight | 0.9112311 | Flight_Change |
| Flight_Change |	I would like to change my flight. |	Flight_Cancel |	0.5517158 |	None |

### Evaluation with the Jupyter Notebook
To get deeper insights into the classification performance, there is a Jupyter notebook in the `notebook` subdirectory. 
1. Open the `Eval - LUIS Scoring Review.ipynb` Jupyter notebook in the `notebook` subfolder of the repository
1. Choose the right kernel `Python (txttool)`, which you installed
1. Place the scoring file from the output folder in the same folder as the notebook or just keep the directory in mind. There is an example file in the notebooks-folder as well
1. Change the file name in the `Import data` section. If you want to reference to the file in the output folder, change it to `../../output/[date-of-case]-case/[date-of-case]-case.txt`.
1. Execute all the fields - this might take a while especially during the plotting phase of the confusion matrix
1. If you want to store the evaluation report, you can do this by "File -> Export -> .html" and open it with any modern internet browser

## Limitations
This toolkit is the right starting point for your bring-your-own data use cases. However, it does not provide automated training runs.