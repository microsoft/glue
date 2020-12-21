''' SPEECH-TO-TEXT USING MICROSOFT SPEECH API '''
''' tiwalz@microsoft.com '''

# Import required packages
import time
import wave
import os
import glob
import sys
import json
import logging
import codecs
import helper as he
import azure.cognitiveservices.speech as speechsdk
import params as pa

# Load and set configuration parameters
pa.get_config()

def request_endpoint(audio, speech_config, output_directory, lexical):
    """Request the speech service endpoint
    Args:
        audio: input data frame
        speech_config: choice between scoring and 
        output_folder: LUIS app ID
        case: LUIS subscription key
        lexical: minimum confidence score for LUIS result, between 0.00 and 1.00
    Returns:
        df: scoring data frame with predicted intents and scores
    Raises:
        ConnectionError: if file is not found
    """
    audio_config = speechsdk.audio.AudioConfig(filename = audio)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config = speech_config, audio_config = audio_config)
    result = speech_recognizer.recognize_once()
    filename = audio[audio.rindex('\\')+1:]
    process_recognition(result, filename, output_directory, lexical)
    return result, filename

def process_recognition(result, filename, output_directory, lexical):
    """
    Process recognition received from the speech service
    """
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        if lexical:
            text = f"{filename}\t{format(result.text)}\t{json.loads(result.json)['NBest'][0]['Lexical']}"
        else:
            text = f"{filename}\t{format(result.text)}"
        logging.warning(f"[INFO] - Recognition successful: {filename} -> {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        logging.warning(filename + "\t" + f"No speech could be recognized: {result.no_match_details}")
        text = ""
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logging.error(filename+"\t"+ f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            logging.error(f"Error details: {cancellation_details.error_details}")
        text = ""
    write_transcription(output_directory, text)

# General Function
def write_transcription(output_directory, text):
    ''' Write transcriptions '''
    if not os.path.exists(f'{output_directory}/transcriptions.txt'):
        transfile = codecs.open(f'{output_directory}/transcriptions.txt', 'w', encoding='utf-8-sig')
        transfile.close()
        logging.warning(f'[INFO] - Created transcript file with utf-8 bom encoding.')
    with open(f"{output_directory}/transcriptions.txt", "a", encoding='utf-8-sig') as transfile:
        transfile.write(f'{text}\n')
        transfile.close()

def main(speech_files, output_directory, lexical = False, enable_proxy = False, *argv):
    """
    Batch-transcribe audio files using speech-to-text
    """
    speech_config = speechsdk.SpeechConfig(subscription = pa.stt_key, region = pa.stt_region)
    # If necessary, you can enable a proxy here: 
    # set_proxy(hostname: str, port: str, username: str, password: str)
    if enable_proxy: 
        speech_config.set_proxy(argv[0], argv[1], argv[2], argv[3])
    # Set speech service properties, requesting the detailed response format to make it compatible with lexical format, if wanted
    speech_config.set_service_property(name='format', value='detailed', channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
    if pa.stt_endpoint != "": 
        speech_config.endpoint_id = pa.stt_endpoint
    logging.info(f'[INFO] - Starting to transcribe {len(next(os.walk(speech_files))[2])} audio files')
    for audio in glob.iglob(f'{speech_files}*av'):
        result, filename = request_endpoint(audio, speech_config, output_directory, lexical)
    # Check the result
    return result, filename

if __name__ == '__main__':
    main("input/audio/", "output/test/")