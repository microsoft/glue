''' SPEECH-TO-TEXT USING MICROSOFT SPEECH API '''
''' nonstoptimm@gmail.com '''

# Import required packages
import os
import glob
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
        audio: Input data frame
        speech_config: Choice between scoring and 
        output_folder: LUIS app ID
        case: LUIS subscription key
        lexical: Minimum confidence score for LUIS result, between 0.00 and 1.00
    Returns:
        df: Scoring data frame with predicted intents and scores
    Raises:
        ConnectionError: If file is not found
    """
    audio_config = speechsdk.audio.AudioConfig(filename = audio)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config = speech_config, audio_config = audio_config)
    result = speech_recognizer.recognize_once()
    filename = audio[audio.rindex('\\')+1:]
    text = process_recognition(result, filename, output_directory, lexical)
    return text, filename

def process_recognition(result, filename, output_directory, lexical):
    """Process recognition received from the speech service
    Args:
        result: Result object returned by STT-service
        filename: Filename for output file
        output_directory: Output directory for the file
        lexical: Boolean to enable extended lexical version of STT-result
    Returns:
        text: Processed recognition as string
    """
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        if lexical:
            text = f"{format(result.text)}\t{json.loads(result.json)['NBest'][0]['Lexical']}"
        else:
            text = f"{format(result.text)}"
        logging.info(f"[INFO] - Recognition successful: {filename} -> {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        logging.warning(filename + "\t" + f"No speech could be recognized: {result.no_match_details}")
        text = ""
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logging.error(filename+"\t"+ f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            logging.error(f"Error details: {cancellation_details.error_details}")
        text = ""
    return text

# General Function
def write_transcription(output_directory, text):
    """Write transcription to file
    Args:
        text: Processed recognition as string
        output_directory: Output directory for the file
    Returns:
        Writes output to file
    """
    if not os.path.exists(f'{output_directory}/transcriptions.txt'):
        transfile = codecs.open(f'{output_directory}/transcriptions.txt', 'w', encoding='utf-8-sig')
        transfile.close()
        logging.warning(f'[INFO] - Created transcript file with utf-8 bom encoding.')
    with open(f"{output_directory}/transcriptions.txt", "a", encoding='utf-8-sig') as transfile:
        transfile.write(f'{text}\n')
        transfile.close()

def main(speech_files, output_directory, lexical = False, enable_proxy = False, *argv):
    """Main function for STT-functionality
    Args:
        speech_files: Directory of audio files to be transcribed
        output_directory: Output directory for the file
        lexical: Boolean to enable extended lexical version of STT-result
        enable_proxy: Boolean to enable proxy function in case you need it
        *argv: Proxy information if enable_proxy is True -> hostname: str, port: str, username: str, password: str
    Returns:
        zip(filenames, results): Zipped lists of filenames and STT-results as string
    """
    try:
        speech_config = speechsdk.SpeechConfig(subscription = pa.config_data['stt_key'], region = pa.config_data['stt_region'])
    except RuntimeError:
        logging.error("[ERROR] - Could not retrieve speech config")
    # If necessary, you can enable a proxy here: 
    # set_proxy(hostname: str, port: str, username: str, password: str)
    if enable_proxy: 
        speech_config.set_proxy(argv[0], argv[1], argv[2], argv[3])
    # Set speech service properties, requesting the detailed response format to make it compatible with lexical format, if wanted
    speech_config.set_service_property(name='format', value='detailed', channel=speechsdk.ServicePropertyChannel.UriQueryParameter)
    if pa.config_data['stt_endpoint'] != "": 
        speech_config.endpoint_id = pa.config_data['stt_endpoint']
    logging.info(f'[INFO] - Starting to transcribe {len(next(os.walk(speech_files))[2])} audio files')
    results = []
    filenames = []
    for audio in glob.iglob(f'{speech_files}*av'):
        result, filename = request_endpoint(audio, speech_config, output_directory, lexical)
        results.append(result)
        filenames.append(filename)
    # Check the result
    return zip(filenames, results)

if __name__ == '__main__':
    main("input/audio/", "output/test/")