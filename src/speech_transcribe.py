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
import helper as he
import azure.cognitiveservices.speech as speechsdk

# Function for Standard Model
def batch_transcribe(speech_files, output_folder, case, service_region, speech_key, endpoint_id = "", enable_proxy = False, lexical = True, *argv):
    """
    Batch-transcribe audio files using speech-to-text
    """
    speech_config = speechsdk.SpeechConfig(subscription = speech_key, region = service_region)
    if enable_proxy:
        speech_config.set_proxy(argv[0], argv[1], argv[2], argv[3])
    # Detailed result, with lexical etc.
    speech_config.set_service_property(name='format', value='detailed', channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
    if endpoint_id != "": speech_config.endpoint_id = endpoint_id
    logging.warning(f'[INFO] - Starting to transcribe {len(next(os.walk(speech_files))[2])} audio files')
    for audio in glob.iglob(f'{speech_files}*av'):
        result, filename = requestEndpoint(audio, speech_config, output_folder, case, lexical)
    # Check the result
    return result, filename

def request_endpoint(audio, speech_config, output_folder, case, lexical):
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
    process_recognition(result, filename, output_folder, case, lexical)
    return result, filename

def process_recognition(result, filename, output_folder, case, lexical):
    """
    Process recognition received from the speech service
    """
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        if lexical:
            text = f"{filename}\t{format(result.text)}\t{json.loads(result.json)['NBest'][0]['Lexical']}"
            print(json.dumps(result.json))
        else:
            text = f"{filename}\t{format(result.text)}"
        logging.warning(f"[INFO] - Recognition successful: {filename} -> {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        logging.warning(filename + "\t" + f"No speech could be recognized: {result.no_match_details}")
        text = ""
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logging.warning(filename+"\t"+ f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            logging.warning(f"Error details: {cancellation_details.error_details}")
        text = ""
    he.writeTranscription(output_folder, case, text)