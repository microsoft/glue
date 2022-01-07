<img src="assets/img/glue_logo.png" alt="GLUE" width="400px">

## About GLUE
GLUE is a lightweight, Python-based collection of scripts to support you at succeeding with speech and text use-cases based on [Microsoft Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/). It not only allows you to batch-process data, but also glues together the services of your choice in one place and ensures an end-to-end view on the training and testing process.

### Modules
GLUE consists of multiple modules, which either can be executed separately or ran as a central pipeline:
- Batch-transcribe audio files to text transcripts using [Microsoft Speech to Text Service](https://azure.microsoft.com/en-us/services/cognitive-services/speech-to-text/) (STT).
- Batch-synthesize text data using [Microsoft Text to Speech Service](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/) (TTS).
- Batch-evaluate reference transcriptions and recognitions.
- Batch-score text strings on an existing, pre-trained [Microsoft LUIS](https://luis.ai)-model.

WIP:
- Batch-translate text data using [Microsoft Translator](https://azure.microsoft.com/en-us/services/cognitive-services/translator/).

### Potential Use-Cases
The toolkit has been built based on our experience from the field and is a great add-on, but not limited, to the following use-cases: 
- Automatized generation of synthetic speech-model training data.
- Batch-transcription of audio files and evaluation given an existing reference transcript.
- Scoring of STT-transcriptions on an existing LUIS-model.

### (Optional) Batch-Generation of Textual Training Data
Based on our experience in the field, we see that often a larger corpus of training data is needed for STT engines and LUIS models. The correct transcription and recognition of entities such as cities and names often play a significant role. Sometimes there is a lack of training data here, which is why we have created a small tool for duplicating utterances based on different entity types. If this also applies to your use-case, then we recommend taking a look at this [Jupyter Notebook](<notebooks/Data - Training Data Generator.ipynb>), which will guide you through the necessary steps.

## Getting Started
This section describes how you get started with GLUE and which requirements need to be fulfilled by your working environment.
If you would like to add your own features and maintain the code in a private repository, you may use the _Template_ function (hit the green button _Use this template_ on the top left).

### Prerequisites
Before getting your hands on the toolkits, make sure your local computer is equipped with the following frameworks and base packages:
- [Python](https://www.python.org/downloads/) (required, Version >=3.8 is recommended).
- [VSCode](https://code.visualstudio.com/) (recommended), but you can also run the scripts using PowerShell, Bash etc.
- Stable connection for installing your environment and scoring the files.
- [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases) for audio file conversion (only for TTS use cases).
  - If you are using Windows, download it from [here](https://ffmpeg.org/download.html#build-windows) and see the description [here](GET_YOUR_KEYS.md).
  - In case you are using Linux, you can install it via command line using a package manager, such as `apt-get install ffmpeg`.

### Setup of Virtual Environment
1. Open a command line of your choice (PowerShell, Bash).
2. Change the directory to your preferred workspace (using `cd`).
3. Clone the repository (alternatively, download the repository. as a zip-archive and unpack your file locally to the respective folder).
```
git clone https://github.com/microsoft/glue
```
4. Enter the root folder of the cloned repository.
```
cd glue
```
5. Set up the virtual environment.
``` 
python -m venv .venv
```
6. Activate the virtual environment.
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
8. (optional) If you want to use Jupyter Notebooks, you can register your activated environment using the command below.
```bash
python -m ipykernel install --user --name glue --display-name "Python (glue)"
```
After successfully installing the requirements-file, your environment is set up and you can go ahead with the next step.

### API Keys
In the root directory of the repository, you can find a file named `config.sample.ini`. This is the file where the API keys and some other essential confirguation parameters have to be set, depending on which services you would like to use. First, create a copy of `config.sample.ini` and rename it to `config.ini` in the same directory. You only need the keys for the services you use during your experiment. However, keep the structure of the `config.ini`-file as it is to avoid errors. The toolkit will just set the values as empty, but will throw an error when the keys cannot be found at all.

An instruction on how to get the keys can be found [here](GET_YOUR_KEYS.md).

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
- Retrieves high-quality audio file from the API and converts it to the Microsoft speech format as well as a version underlaid by the noise of a telephone line.
- Functionality is limited to the languages and fonts listed on the [language support](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support#text-to-speech) page.
- Make sure the voice of your choice is available in the respective Azure region ([see documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech#standard-and-neural-voices)).

`luis.py`
- Batch-scoring of intent-text combinations using an existing LUIS model.
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
| __TTS__            | `--do_synthesize`          | Activate text-to-speech synthetization.                                  | Requires csv file with `text`-column, see `--audio_files`.                                                                                                                                      |
| __STT__            | `--do_transcribe`          | Activate speech-to-text processing.                                      | Requires audio files, see `--audio_files`.                                                                                                                                                      |
| __STT__            | `--audio_files`            | Path to folder with audio files.                                         | Audio files have to be provided as WAV-file with the parameters described [here](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/how-to-custom-speech-test-and-train). |
| __STT-Evaluation__ | `--do_evaluate`            | Activate evaluation of transcriptions based on reference transcriptions. | Requires csv-file with `text`-column and intent names.                                                                                                                                          |
| __LUIS__           | `--do_scoring`             | Activate LUIS model scoring.                                             | Requires csv-file with `intent` (ground truth of LUIS intent) and `text` columns (max. 500 characters due to LUIS limitation, gets cut if > 500 characters.                                                                                                                                             |
| __STT / TTS__      | `--input`                  | Path to comma-separated text input file.                                 |                                                                                                                                                                                                |


### Input File Guidelines
Depending on your use-case described in the table above, you may have to provide an input text file and/or audio files. In these cases, you have to pass the path to the respective input file of folder via command line. Following guidelines exist for these input files:
- Comma-separated values (csv) file (if you only have an Excel sheet, you can export it as csv-file: (_Save as_ -> _CSV UTF-8 (Comma delimited (*.csv))_).
- UTF-8 encoding (to make sure it has the correct encoding, open it with a text editor such as [Notepad++](https://notepad-plus-plus.org/downloads/) -> Encoding -> Convert to UTF-8).
- Column names (depending on the module it may be a mix of the following: `text` (utterance of the text, max length of 500 characters) and/or `intent` (ground-truth LUIS-intent) and/or `audio`).
- We recommend you to put the input file in a subfolder called `input`, but you can choose arbitrary here.

You can find an [example text files](assets/examples/input_files) as well as [example audio files](assets/examples/input_files/audio/) following the respective links.

### Output
GLUE creates multiple folders and files of different types, depending on the modes you want it to run. The overview table below shows you which folders and files it may cover. Folders end with a `/`, files wend with a file ending (e.g. _.csv_). The _X_ in the respective mode columns indicate, given which mode the output files and folders are created.

| __File / Folder__           | STT | TTS | LUIS | Eval | Comment |
|-----------------------------|-----|-----|------|------|------|
| __luis_scoring.csv__        |     |     |   X  |      | Comma-separated file with audio file names and transcriptions.     |
| __stt_transcriptions.txt__  |  X  |     |      |      | Tab-delimited file with audio file names and transcriptions. |
| __tts_transcriptions.txt__  |     |  X  |      |      | Tab-delimited file with audio file names and transcriptions.|
| __tts_transcriptions.csv__  |     |  X  |      |      | Comma-separated file with audio file names and transcriptions.|
| __transcriptions_full.csv__ |  X  |  X  |      |      | Comma-separated file with merged columns of the current run.  |
| __input/__                  |     |  X  |   X  |   X  | Folder with duplicate of input file.     |
| __tts_converted/__          |     |  X  |      |      | Folder with TTS-results in Microsoft Speech-optimized format.     |
| __tts_generated/__          |     |  X  |      |      | Folder with raw, high-quality TTS-results.     |
| __tts_telephone/__          |     |  X  |      |      | Folder with TTS-results in Microsoft Speech-optimized format, underlaid with telephone line sound.     |

## How to use GLUE
The following section describes how to run the individual modules via the orchestrator.

### Scenario 1: Speech-to-Text (STT)
This scenario describes how you can batch-transcribe audio files using GLUE. A potential use case can be that you do not have reference transcriptions to the audio files yet and want to accelerate the transcription-process, by "pre-labeling" the data. The recognitions might not be perfect, but it helps you to have a much better time by providing a starting point.

#### Pre-requisites:
- Azure Speech Service resource (see [Get Your Keys](GET_YOUR_KEYS.md)).
- Audio files in .wav-format in a separate folder, as all wave files in the directory will be collected.
- See example audio files [here](assets/examples/input_files/audio/).

#### Run GLUE
1. `cd` to the root folder of GLUE.
2. Make sure your `.venv` is activated.
3. Run the following command:
```bash
python src/glue.py --audio C:/audio_files/ --do_transcribe
```
4. Wait for the run to finish.

#### Output
GLUE will create an output folder as below:
```
- case: [YYYYMMDD]-[UUID]/
 | -- stt_transcriptions.txt (tab-delimited file with audio file names and transcriptions)
```

### Scenario 2: Text-to-Speech (TTS)
This scenario describes how you can batch-synthesize text data using GLUE. A potential use case can be that you want to create synthetic training data for your speech model, as you do not have enough speakers to create acoustic training material. The use case may be callcenter-related, which is why you need some tweaked data in order to simulate a realistic setup.

#### Pre-requisites
- Azure Speech Service resource (see [Get Your Keys](GET_YOUR_KEYS.md)).
- Textual, comma-separated input file with a `text` column and utterances to be synthesized.
- See an example input file [here](assets/examples/input_files/example_tts.csv).

#### Run GLUE
1. `cd` to the root folder of GLUE.
2. Make sure your `.venv` is activated.
3. Run the following command:
```bash
python src/glue.py --input ../input-files/text.csv --do_synthesize
```
4. Wait for the run to finish.

#### Output
GLUE will create an output folder as below:
```
- case: [YYYYMMDD]-[UUID]/
  | -- input/
    | -- [input text file].csv
  | -- tts_converted
    | -- [converted audio files]
    | -- [converted audio files]
  | -- tts_generated
    | -- [generated audio files]
    | -- [generated audio files]
  | -- tts_telephone
    | -- [modified audio files]
    | -- [modified audio files]
 | -- tts_transcriptions.txt (tab-delimited file with audio file names and transcriptions)
 | -- tts_transcriptions.csv (comma-separated file with audio file names and transcriptions)
```

### Scenario 3: LUIS-Scoring
This scenario shows how you can use GLUE to batch-score textual data on a LUIS-endpoint.

#### Pre-requisites
- LUIS app and the respective keys (see [Get Your Keys](GET_YOUR_KEYS.md)).
  - If you do not have a LUIS app yet, you can use our [example LUIS app for flight bookings](assets/examples/input_files/example-luis-app.lu) and import it to your resource. 
- Textual input file with an `intent` AND `text` column.
- See an example input file [here](assets/examples/input_files/example_luis.csv).

#### Run GLUE
1. `cd` to the root folder of GLUE.
2. Make sure your `.venv` is activated.
3. Run the following command:
```bash
python src/glue.py --input /home/files/luis-utterances.csv --do_scoring
```
4. Wait for the run to finish and see the command line outputs.

#### Output
GLUE will create an output folder as below:
```
- case: [YYYYMMDD]-[UUID]/
  | -- input/
    | -- [input text file].csv
 | -- luis_scoring.csv (comma-separated file with audio file names and transcriptions)
```

In your command line, you will see a print of a [confusion matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html) as well as a [classification report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html). These reports cannot be written to a file, however they are based on the output file `luis-scoring.txt` and you may use the Jupyter notebook to load them again and gain deep insights into the classification performance. The following table shows the structure of the scoring file `luis_scoring.csv` and provides you an example how predictions are handled, also when the confidence score is low.
| intent | text | prediction_text | score_text | prediction_drop_text |
|-|-|-|-|-|
| _Intent name based on reference Excel file_ | _Raw text string_ | _Predicted intent by LUIS app_ | _Certainty score of LUIS model, between 0 and 1_ | _Predicted intent by LUIS app, _None_-intent in case of dropped value (when below the confidence score e.g. of 0.82)_ |
| BookFlight | I would like to book a flight to Frankfurt. | BookFlight | 0.9450068 | BookFlight |
| CancelFlight | I want to cancel my journey to Kuala Lumpur. | CancelFlight | 0.8340548 | CancelFlight |
| ChangeFlight | I would like to change my flight to Singapore. | ChangeFlight | 0.9112311 | ChangeFlight |
| ChangeFlight | I would like to book a seat on my flight to Stuttgart. | BookFlight | 0.5517158 | None |


### Scenario 4: Evaluation
This scenario describes how you can compare already existing recognitions with a ground-truth reference transcription using GLUE. A potential use case can be that you want to assess the quality of your speech model and figure out potential recognition problems, which you may counteract by custom model training. In this case, you have to provide already existing recognitions to the tool.

#### Pre-requisites:
- Azure Speech Service resource (see [Get Your Keys](GET_YOUR_KEYS.md)).
- Textual input file with an `text` column with reference transcriptions as well as a `rec` column with recognitions.
- See an example input file [here](assets/examples/input_files/example_eval.csv).

#### Run GLUE
1. `cd` to the root folder of GLUE.
2. Make sure your `.venv` is activated.
3. Run the following command:
```bash
python src/glue.py --input ../input/transcriptions.txt --do_evaluate
```
4. Wait for the run to finish and see the command line outputs.

#### Output
GLUE will create an output folder as below:
```
- case: [YYYYMMDD]-[UUID]/
 | -- input/
    | -- [input text file].csv
 | -- transcriptions_full.csv (comma-separated file with merged columns of the current run)
```

In your command line, you will see an output of the evaluation algorithms per sentence as well as an overall summary in case you used multiple utterances. These evaluations are based on the `text` and `rec` columns. As the command line output is only temporary, we recommend you to use the Jupyter Notebook resulting from this run.

### Scenario 5: Speech to Text and Evaluation
This scenario describes how you can batch-transcribe audio files and compare these recognitions with a ground-truth reference transcription using GLUE. A potential use case can be that you want to assess the quality of your speech model and figure out potential recognition problems, which you may counteract by custom model training.

#### Pre-requisites:
- Azure Speech Service resource (see [Get Your Keys](GET_YOUR_KEYS.md)).
- Audio files in .wav-format in a dedicated folder, as all wave files in the directory will be collected
- Textual input file with an `audio` column for reference audio file names AND the respective `text` column with reference transcriptions.
- See an example input file [here](assets/examples/input_files/example_stt_eval.csv) and example audio files [here](assets/examples/input_files/audio//).

#### Run GLUE
1. `cd` to the root folder of GLUE.
2. Make sure your `.venv` is activated.
3. Run the following command:
```bash
python src/glue.py --audio C:/audio_files/ --input C:/audio_files/transcriptions.txt --do_transcribe --do_evaluate
```
4. Wait for the run to finish and see the command line outputs.

#### Output
GLUE will create an output folder as below:
```
- case: [YYYYMMDD]-[UUID]/
 | -- input/
    | -- [input text file].csv
 | -- stt_transcriptions.txt (tab-delimited file with audio file names and transcriptions)
 | -- transcriptions_full.csv (comma-separated file with merged columns of the current run)
```

### Scenario 6: Speech to Text, Evaluation and LUIS-Scoring
This scenario describes how you can batch-transcribe audio files, compare these recognitions with a ground-truth reference transcription and score both version on a LUIS-endpoint using GLUE. A potential use case can be that you want to assess the quality of your speech model, figure out potential recognition problems and also compare the impact on a LUIS model using STT in between.

#### Pre-requisites:
- Azure Speech Service resource (see [Get Your Keys](GET_YOUR_KEYS.md)).
- LUIS app and the respective keys (see [Get Your Keys](GET_YOUR_KEYS.md)).
  - If you do not have a LUIS app yet, you can use our [example LUIS app for flight bookings](assets/examples/input_files/example-luis-app.lu) and import it to your resource. 
- Audio files in .wav-format in a dedicated folder, as all wave files in the directory will be collected.
- Textual input file with an `audio` column for reference audio file names AND `intent` for the LUIS class AND the respective `text` column with reference transcriptions.
- See an example input file [here](assets/examples/input_files/example_stt_eval_luis.csv) and example audio files [here](assets/examples/input_files/input/audio//).

#### Run GLUE
1. `cd` to the root folder of GLUE.
2. Make sure your `.venv` is activated.
3. Run the following command:
```bash
python src/glue.py --audio C:/audio_files/ --input C:/audio_files/transcriptions.txt --do_transcribe --do_evaluate --do_scoring
```
4. Wait for the run to finish and see the command line outputs.

#### Output
GLUE will create an output folder as below:
```
- case: [YYYYMMDD]-[UUID]/
 | -- input/
    | -- [input text file].csv
 | -- luis_scoring.csv (comma-separated file with audio file names and transcriptions)
 | -- stt_transcriptions.txt (tab-delimited file with audio file names and transcriptions)
 | -- transcriptions_full.csv (comma-separated file with merged columns of the current run)
```

In your command line, you will see a print of a [confusion matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html) as well as a [classification report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html). These reports cannot be written to a file, however they are based on the output file `luis-scoring.txt` and you may use the Jupyter notebook to load them again and gain deep insights into the classification performance. The following table shows the structure of the scoring file `luis_scoring.csv` and provides you an example how predictions are handled, also when the confidence score is low.
Compared to scenario 3, where only the reference text was scored, the `luis-scoring.txt`-file will have more columns this time. Each of the columns `prediction_`, `score_`, `prediction_drop_` will have a `text` (reference transcript) and `rec` (recognition) version. This is supposed to help you evaluating the differences in LUIS recognition given different inputs. Intent predictions and scores may differ given irregularities in transcribing audio files. We invented some transcription issues, which you see below, _highlighted_ in column _rec_.
| intent | text | rec | prediction_{text/rec} | score_{text/rec} | prediction_drop_{text/rec} |
|-|-|-|-|-|-|
| _Intent name based on reference Excel file_ | _Raw text string_ | STT recognition | _Predicted intent by LUIS app_ | _Certainty score of LUIS model, between 0 and 1_ | _Predicted intent by LUIS app, _None_-intent in case of dropped value (when below the confidence score e.g. of 0.82)_ |
| BookFlight | I would like to book a flight to Frankfurt. | I would like to book a _fight_ to Frankfurt. | BookFlight | 0.9450068 | BookFlight |
| CancelFlight | I want to cancel my journey to Kuala Lumpur. | I _wanna_ cancel my journey to kualalumpur. | CancelFlight | 0.8340548 | CancelFlight |
| ChangeFlight | I would like to change my flight to Singapore. | Would like to change _mum_ flight to Singapore. | ChangeFlight | 0.9112311 | ChangeFlight |
| ChangeFlight | I would like to book a seat on my flight to Stuttgart. | I would like to book a _suite_ on my flight to Stuttgart. | BookFlight | 0.5517158 | None |

### Scenario 7: Speech to Text and LUIS-Scoring
This scenario describes how you can batch-transcribe audio files and score both version on a LUIS-endpoint using GLUE. A potential use case can be that you want to assess the quality of your LUIS model using STT as a reference and in case you do not have a reference transcription. However, you need an `intent` column for every input audio file.

#### Pre-requisites:
- Azure Speech Service resource (see [Get Your Keys](GET_YOUR_KEYS.md)).
- LUIS app and the respective keys (see [Get Your Keys](GET_YOUR_KEYS.md)).
  - If you do not have a LUIS app yet, you can use our [example LUIS app for flight bookings](assets/examples/input_files/example-luis-app.lu) and import it to your resource. 
- Audio files in .wav-format in a dedicated folder, as all wave files in the directory will be collected.
- Textual input file with an `audio` column for reference audio file names AND `intent` for the LUIS class.
- See an example input file [here](assets/examples/input_files/example-stt-luis.csv).

#### Run GLUE
1. `cd` to the root folder of GLUE.
2. Make sure your `.venv` is activated.
3. Run the following command:
```bash
python src/glue.py --audio C:/audio_files/ --input C:/audio_files/transcriptions.txt --do_transcribe --do_scoring
```
4. Wait for the run to finish and see the command line outputs.

#### Output
GLUE will create an output folder as below:
```
- case: [YYYYMMDD]-[UUID]/
 | -- input/
    | -- [input text file].csv
 | -- luis_scoring.csv (comma-separated file with audio file names and transcriptions)
 | -- stt_transcriptions.txt (tab-delimited file with audio file names and transcriptions)
 | -- transcriptions_full.csv (comma-separated file with merged columns of the current run)
```

In your command line, you will see a print of a [confusion matrix](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html) as well as a [classification report](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html). These reports cannot be written to a file, however they are based on the output file `luis-scoring.txt` and you may use the Jupyter notebook to load them again and gain deep insights into the classification performance. The following table shows the structure of the scoring file `luis_scoring.csv` and provides you an example how predictions are handled, also when the confidence score is low.
Compared to scenario 3, where only the reference utterances were scored, the columns `prediction_`, `score_`, `prediction_drop_` of `luis_scoring.csv`-file will end with `rec` (recognition) instead of `text` (reference transcript) in this case.

| intent | rec | prediction_rec | score_rec | prediction_drop_rec |
|-|-|-|-|-|
| _Intent name based on reference Excel file_ | _STT result_ | _Predicted intent by LUIS app_ | _Certainty score of LUIS model, between 0 and 1_ | _Predicted intent by LUIS app, _None_-intent in case of dropped value (when below the confidence score e.g. of 0.82)_ |
| BookFlight | I would like to book a fight to Frankfurt. | BookFlight | 0.8750068 | BookFlight |
| CancelFlight | I want to cancel my journey to kualalumpur. | CancelFlight | 0.7140548 | None |
| ChangeFlight | Would like to change my flight to Singapore. | ChangeFlight | 0.8992311 | ChangeFlight |
| ChangeFlight | I would like to book a suite on my flight to Stuttgart. | BookFlight | 0.3917158 | None |

We can see that the recognition scores have decreased, so this may have an impact on the overall recognition rate.

## Limitations
> This toolkit is the right starting point for your bring-your-own data use cases. However, it does not provide automated training runs and does not ensure an improvement of the performance on your task. It helps you to do end-to-end testing and gain the right insights on how to improve the quality on your use-case.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
