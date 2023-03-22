''' GLUE - THE TOOLKIT FOR MICROSOFT COGNITIVE SERVICES '''
''' nonstoptimm@gmail.com '''
''' Supports Text-To-Speech (TTS), Speech-To-Text (STT), Evaluation, LUIS-Scoring '''

# Import standard packages
import os
import sys
import shutil
import logging
import argparse
import pandas as pd

# Import custom modules
import stt
import tts
import luis_scoring as luis
import params as pa
import helper as he
import evaluate as eval

''' COMMAND EXAMPLES '''
# python .\src\glue.py --do_synthesize --input input/scoringfile.txt

# Parse arguments
parser = argparse.ArgumentParser()
args = pa.get_params(parser)

# Set arguments
fname = args.input
audio_files = args.audio
do_synthesize = args.do_synthesize
do_scoring = args.do_scoring
do_transcribe = args.do_transcribe
do_evaluate = args.do_evaluate

# Get config from file
pa.get_config()

# Set logging level to INFO
logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    logging.info('[INFO] - Starting GLUE - v0.2.2')

    # Case Management
    if any([do_scoring, do_synthesize, do_transcribe, do_evaluate]):
        output_folder, case = he.create_case(pa.config_data['output_folder'])
        logging.info(f'[INFO] - Created case {case}')
        try:
            os.makedirs(f"{output_folder}/{case}/input", exist_ok=True)
            shutil.copyfile(fname, f'{output_folder}/{case}/input/{os.path.basename(fname)}')
            df_reference = pd.read_csv(f'{output_folder}/{case}/input/{os.path.basename(fname)}', sep=',', encoding='utf-8', index_col=None)
            logging.info(f'[INFO] - Copied input file(s) to case folder')
        except Exception as e:
            if do_synthesize or do_scoring:
                logging.error(f'[ERROR] - Error with input file or FileNotFound, but it is required for --do_transcribe and/or --do_scoring -> {e}')
                sys.exit()
            else:
                logging.warning('[WARNING] - Could not find input file, but we can continue here')
                df_reference = pd.DataFrame()
    else:
        logging.error('[ERROR] - Please activate at least one of the following modes: --do_synthesize, --do_transcribe, --do_scoring, --do_evaluate (see --help for further information)!')
        sys.exit()

    # TTS
    if do_synthesize:
        logging.info(f'[INFO] - Starting text-to-speech synthetization of {len(df_reference)} utterances')
        df_reference = tts.main(df_reference, f'{output_folder}/{case}')
        df_reference[['audio_synth', 'text']].to_csv(f'{output_folder}/{case}/tts_transcription.txt', sep = "\t", header = None, index = False)
        df_reference[['audio_synth', 'text']].to_csv(f'{output_folder}/{case}/tts_transcription.csv', sep = ",", index = False)
        logging.info(f'[INFO] - Finished text-to-speech synthetization of {len(df_reference)} utterances and wrote output files')

    # STT
    if do_transcribe:
        if audio_files != None:
            logging.info('[INFO] - Starting with speech-to-text conversion')
            stt_results = stt.main(f'{audio_files}/', f'{output_folder}/{case}')
            df_transcription = pd.DataFrame(list(stt_results), columns=['audio', 'rec'])
            logging.debug(df_transcription)
            df_transcription.to_csv(f'{output_folder}/{case}/stt_transcriptions.txt', sep = '\t', header = None, index=False)
            # Merge reference transcriptions with recognition on audio file names
            if 'audio' in list(df_reference.columns):
                df_reference = pd.merge(left = df_reference, right = df_transcription, how = 'left', on = 'audio')
                logging.info(f'[INFO] - Merged imported reference transcriptions and recognitions')
                df_reference.to_csv(f'{output_folder}/{case}/transcriptions_full.csv', sep = ',', encoding = 'utf-8', index = False)
                logging.info(f'[INFO] - Wrote transcription file to case folder')
        else:
            logging.error('[ERROR] - It seems like you did not pass a path to audio files, cannot do transcriptions')
            sys.exit()

    # Speech Evaluation
    if do_evaluate:
        logging.info('[INFO] - Starting with reference vs. recognition evaluation')
        if 'text' in list(df_reference.columns) and 'rec' in list(df_reference.columns):
            eval.main(df_reference)
            logging.info('[INFO] - Evaluated reference and recognition transcriptions')
        else:
            logging.error('[ERROR] - Cannot do evaluation, please verify that you both have "text" and "rec" in your data!')

    # LUIS Scoring
    if do_scoring:
        logging.info('[INFO] - Starting with LUIS scoring')
        logging.info(f'[INFO] - Set LUIS treshold to {pa.config_data["luis_treshold"]}')
        if 'intent' in list(df_reference.columns) and not 'rec' in list(df_reference.columns):
            luis_scoring = luis.main(df_reference, 'text')
        elif all(['intent' in list(df_reference.columns), 'rec' in list(df_reference.columns)]):
            luis_scoring = luis.main(df_reference, 'text')
            luis_scoring = luis.main(df_reference, 'rec')
        elif 'intent' in list(df_reference.columns) and not 'text' in list(df_reference.columns):
            luis_scoring = luis.main(df_reference, 'rec')
        else:
            logging.error('[ERROR] - Cannot do LUIS scoring, please verify that you have an "intent"-column in your data.')
        # Write to output file
        luis_scoring['luis_treshold'] = pa.config_data['luis_treshold']
        luis_scoring.to_csv(f'{output_folder}/{case}/luis_scoring.csv', sep = ',', encoding = 'utf-8', index=False)

    # Finish run
    logging.info(f'[INFO] - Finished with the run {case}!')