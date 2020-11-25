''' NLP TOOLS FOR MICROSOFT COGNITIVE SERVICES '''
''' tiwalz@microsoft.com '''
''' Supports Text-To-Speech, Speech-To-Text and LUIS-Scoring '''

# Import required packages
import logging
import argparse
import os
import sys
import configparser
import shutil
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

# 
import evaluate as ev
import helper as he
import score_luis as sl
import speech_transcribe as stt
import synthesize_text as tts
import collect_params as pa

''' COMMAND EXAMPLES '''
# python .\code\main.py --do_synthesize --input input/scoringfile.txt

# Parse arguments
parser = argparse.ArgumentParser()
args = pa.get_params(parser)

# Set arguments
fname = args.input
mode = args.mode
subfolder = args.subfolder
treshold = args.treshold
audio_files = args.audio_files
do_synthesize = args.do_synthesize
do_scoring = args.do_scoring
do_transcribe = args.do_transcribe
do_evaluate = args.do_evaluate
do_lufile = args.do_lufile

# Get config
pa.get_config()

# Set logger
logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    logging.info('[INFO] - STARTING SPEECHTOOL')
    # Case management
    try:
        if any([do_scoring, do_synthesize, do_transcribe, do_evaluate]):
            output_folder, case, output_file = he.create_case(mode, pa.output_folder, subfolder)
            if do_synthesize or do_scoring: 
                shutil.copyfile(fname, f'{output_folder}{case}input/{os.path.basename(fname)}')
            logging.info(f'[INFO] - Created case {case} and copied input files to case folder')
        else:
            logging.error('[ERROR] - Please activate at least one of the following modes: --do_synthesize, --do_transcribe, --do_scoring, --do_evaluate (see --help for further information)!')
            sys.exit()
    except Exception as e:
        logging.error(f'[ERROR] -> {e}')

    # File reader
    try:
        df = pd.read_csv(f'{output_folder}{case}input/{os.path.basename(fname)}', sep='\t', encoding='utf-8', index_col=None)
    except FileNotFoundError as e:
        logging.error(f'[ERROR] - Please pass an input file!')

    # TTS
    if do_synthesize:
        logging.info('[STATUS] - Starting text-to-speech synthetization')
        df = tts.batch_synthesize(df, pa.synth_key, pa.language, pa.font, pa.region_synth, pa.resource_name, output_folder, case)
        logging.info(f'[STATUS] - Finished text-to-speech synthetization of {len(df)} utterances')

    # STT
    if do_transcribe:
        if audio_files != "":
            logging.info('[STATUS] - Starting with speech-to-text conversion')
            stt.batch_transcribe(audio_files, output_folder, case, pa.region_speech, pa.speech_key, pa.endpoint)
            transcription = pd.read_csv(f'{output_folder}{case}transcriptions.txt', sep="\t", names=['audio', 'rec'], encoding='utf-8', header=None, index_col=None)
            if 'audio' in list(df.columns):
                df = pd.merge(left=df, right=transcription, how='left', on='audio')

    # Speech Evaluation
    if do_evaluate:
        logging.info('[STATUS] - Starting with ref/rec evaluation')
        if 'text' in list(df.columns) and 'rec' in list(df.columns):
            df.text = df.text.fillna("")
            df.rec = df.rec.fillna("")
            eva = ev.EvaluateTranscription()
            eva.calculate_metrics(df.text.values, df.rec.values, label=df.index.values, print_verbosiy=2)
            eva.print_errors(min_count=1)
        else:
            logging.error('[ERROR] - Cannot do evaluation, please verify that you both have "ref" and "rec" in your data!')

    # LUIS Scoring
    if do_scoring and 'intent' in list(df.columns):
        if mode == 'score':
            logging.info('[STATUS] - Starting with LUIS scoring')
            data = sl.score_endpoint(df, mode, pa.app_id, pa.luis_endpoint, pa.key, pa.slot, treshold)
            data.to_csv(output_file, sep='\t', encoding='utf-8', index=False)
        elif mode == 'eval':
            logging.info('[STATUS] - Starting with LUIS eval')
            data = pd.read_csv(fname, sep='\t', encoding='utf-8')
        # Classification Report
        print('[OUTPUT] - CLASSIFICATION REPORT (without reset by treshold):')
        print(classification_report(data['intent'], data['prediction']))
        print(f'[OUTPUT] - AFTER RESET BY TRESHOLD ({treshold}):')
        print(classification_report(data['intent'], data['drop']))
        print('[OUTPUT] - CONFUSION MATRIX:')
        print(confusion_matrix(data['intent'], data['prediction']))

    # Write transcript file
    try:
        df.to_csv(f'{output_folder}{case}transcriptions_full.txt', sep="\t", encoding="utf-8", index=False)
        logging.info(f'[INFO] - Wrote transcription file to case.')
        logging.info(f'[STATUS] - All set!')
    except Exception as e:
        logging.error(f'[ERROR] - An error has occured -> {e}.')
