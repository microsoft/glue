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

# 
import evaluate as eval
import helper as he
import score_luis as luis
import speech_transcribe as stt
import synthesize_text as tts
import params as pa

''' COMMAND EXAMPLES '''
# python .\src\main.py --do_synthesize --input input/scoringfile.txt

# Parse arguments
parser = argparse.ArgumentParser()
args = pa.get_params(parser)

# Set arguments
fname = args.input
subfolder = args.subfolder
luis_treshold = args.treshold
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
    logging.info('[INFO] - Starting Cognitive Services Tools - v0.1')
    # Case management
    if any([do_scoring, do_synthesize, do_transcribe, do_evaluate]):
        output_folder, case, output_file = he.create_case(pa.output_folder, subfolder)
        logging.info(f'[INFO] - Created case {case}')
        try:
            shutil.copyfile(fname, f'{output_folder}/{case}/input/{os.path.basename(fname)}')
            df = pd.read_csv(f'{output_folder}/{case}/input/{os.path.basename(fname)}', sep=';', encoding='utf-8', index_col=None)
            logging.info(f'[INFO] - Copied input file(s) to case folder')
        except FileNotFoundError as fnf:
            if do_synthesize or do_scoring:
                logging.error('[ERROR] - Could not find input file, but it is required for --do_transcribe and/or --do_scoring')
                sys.exit()
            else:
                logging.warning('[WARNING] - Could not find input file, but we can continue here')
    else:
        logging.error('[ERROR] - Please activate at least one of the following modes: --do_synthesize, --do_transcribe, --do_scoring, --do_evaluate (see --help for further information)!')
        sys.exit()

    # TTS
    if do_synthesize:
        logging.info(f'[STATUS] - Starting text-to-speech synthetization of {len(df)} utterances.')
        df = tts.main(df, f'{output_folder}/{case}', pa.stt_endpoint)
        logging.info(f'[STATUS] - Finished text-to-speech synthetization of {len(df)} utterances.')

    # STT
    if do_transcribe:
        if audio_files != "":
            logging.info('[STATUS] - Starting with speech-to-text conversion')
            stt.main(audio_files, output_folder, case, pa.region_speech, pa.speech_key, pa.endpoint)
            transcription = pd.read_csv(f'{output_folder}{case}transcriptions.txt', sep="\t", names=['audio', 'rec'], encoding='utf-8', header=None, index_col=None)
            if 'audio' in list(df.columns):
                df = pd.merge(left=df, right=transcription, how='left', on='audio')

    # Speech Evaluation
    if do_evaluate:
        logging.info('[STATUS] - Starting with ref/rec evaluation')
        if 'text' in list(df.columns) and 'rec' in list(df.columns):
            eval.main(df)
        else:
            logging.error('[ERROR] - Cannot do evaluation, please verify that you both have "ref" and "rec" in your data!')

    # LUIS Scoring
    if do_scoring and 'intent' in list(df.columns):
        logging.info('[STATUS] - Starting with LUIS scoring')
        luis_scoring = luis.main(df, luis_treshold, luis_mode)
        data.to_csv(output_file, sep='\t', encoding='utf-8', index=False)        

    # Write transcript file
    try:
        df.to_csv(f'{output_folder}{case}transcriptions_full.txt', sep="\t", encoding="utf-8", index=False)
        logging.info(f'[INFO] - Wrote transcription file to case.')
        logging.info(f'[STATUS] - All set!')
    except Exception as e:
        logging.error(f'[ERROR] - An error has occured -> {e}.')
