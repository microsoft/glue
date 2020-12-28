![GLUE](assets/img/glue_logo.png)

## About GLUE
GLUE is a lightweight, Python-based collection of scripts to support you at succeeding with speech and text use-cases based on [Microsoft Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/). It not only allows you to batch-process data, rather glues together the services of your choice in one place and ensures an end-to-end view on the training and testing process.

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
- Retrieves high-quality audio file from the API and converts it to the Microsoft speech format as well as a version underlaid by the noise of a telephone line
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
- In case there is a need for custom components, we recommend to add them to this module.
- Creates folder for every run using the naming convention `YYYYMMDD-[unique ID]`.

### Input Parameters
The following table shows and describes the available modes along with their input parameters as well as dependencies.

| __Mode__           | __Command line parameter__ | __Description__                                                         | __Dependencies__                                                                                                                                                                               |
|--------------------|----------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| __TTS__            | `--do_synthesize`          | Activate text-to-speech synthetization                                  | Requires csv file with `text`-column, see `--audio_files`                                                                                                                                      |
| __STT__            | `--do_transcribe`          | Activate speech-to-text processing                                      | Requires audio files, see `--audio_files`                                                                                                                                                      |
| __STT__            | `--audio_files`            | Path to folder with audio files                                         | Audio files have to be provided as WAV-file with the parameters described [here](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-custom-speech-test-and-train) |
| __STT-Evaluation__ | `--do_evaluate`            | Activate evaluation of transcriptions based on reference transcriptions | Requires csv-file with `text`-column and intent names                                                                                                                                          |
| __LUIS__           | `--do_scoring`             | Activate LUIS model scoring                                             | Requires csv-file with `intent` (ground truth of LUIS intent) and `text` columns (max. 500 characters due to LUIS limitation, gets cut if > 500 characters)                                                                                                                                             |
| __STT / TTS__      | `--input`                  | Path to comma-separated text input file                                 |                                                                                                                                                                                                |


### Input File Guidelines
Depending on your use-case described in the table above, you may have to provide an input text file and/or audio files. In these cases, you have to pass the path to the respective input file of folder via command line. Following guidelines exist for these input files:
- Comma-separated values (csv) file (if you only have an Excel sheet, you can export it as csv-file: (_Save as_ -> comma-separated)
- UTF-8 encoding (to make sure it has the correct encoding, open it with a text editor such as [Notepad++](https://notepad-plus-plus.org/downloads/) -> Encoding -> Convert to UTF-8).
- Column names (depending on the module, `text` or `text` and `intent`).
- of columns _intent_ (ground-truth LUIS-intent) and _text_ (utterance of the text, max length of 500 characters).
- We recommend you to put the input file in the subfolder `input`.

You can find an [example text file](input/testset-example.txt) as well as [example audio files]() following the respective links.

## Run Modules
The following section describes how to run the individual modules via the orchtestrator.

### Scenario 1: Speech-to-Text (STT)

### Scenario 2: Text-to-Speech (TTS)

### Scenario 3: LUIS-Scoring
The following table shows the structure of the scoring file and gives you an example how predictions are handled, also when the confidence score is low.
| intent | text | prediction | score | drop |
| --- | --- | --- | --- | --- |
| Intent name based on reference Excel file | Raw text string | Predicted intent by LUIS app | Certainty score of LUIS model, between 0 and 1 | Predicted intent by LUIS app, _None_-intent in case of dropped value (when below the confidence score e.g. of 0.82) |
| Book_Flight | I would like to book a flight to Frankfurt. |	Book_Flight |	0.9450068 | Book_Flight |
| Flight_Change | Please rebook my flight to Singapore, please | Change_Flight | 0.9112311 | Flight_Change |
| Flight_Change |	I would like to change my flight. |	Flight_Cancel |	0.5517158 |	None |



## Limitations
This toolkit is the right starting point for your bring-your-own data use cases. However, it does not provide automated training runs.