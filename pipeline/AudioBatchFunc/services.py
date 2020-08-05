''' TTS SERVICES '''
import os
import logging
import sys
import time
# Microsoft
import requests
# Google
from google.cloud import texttospeech
# Amazon
import boto3

# Import sub scripts
try:
    from __app__ import helper as he
    from __app__ import audio as au
except Exception as e:
    logging.info('[INFO] Main: Using local imports.')
    sys.path.append('./')
    import AudioBatchFunc.helper as he
    import AudioBatchFunc.audio as au

''' MICROSOFT '''
class TextToSpeech(object):
    def __init__(self, subscription_key, language, font, text, region):
        self.subscription_key = subscription_key
        self.tts = f'<speak version="1.0" xml:lang="en-us"><voice xml:lang="{language}" name="Microsoft Server Speech Text to Speech Voice ({language}, {font})">{text}</voice></speak>'
        self.timestr = time.strftime("%Y%m%d-%H%M")
        self.access_token = None

    def get_token(self, region, subscription_key):
        fetch_token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def save_audio(self, region, resource_name, output_folder, provider, language, font, i, transcribe, transfile):
        url = f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': resource_name
        }
        response = requests.post(url, headers=headers, data=self.tts)
        if response.status_code == 200:
            fname = he.getFilename('generated/', output_folder, provider, language, font, i, 'wav')
            with open(fname, "wb") as audio:
                audio.write(response.content)
                logging.info(f"[INFO] - File {fname} written.")
                if transcribe:
                    transfile.write(f"{os.path.basename(fname)}\t{he.removeTags(self.tts)}\n")
                    logging.info("[INFO] - Transcription written to file.")
            return os.path.basename(fname)
        else:
            logging.error(f"[ERROR] - Status code: {str(response.status_code)} -> something went wrong, please check your subscription key and headers.")
            raise Exception(f"[ERROR] - Could not finish synthetization!")
        
''' GOOGLE '''
def googleTTS(ssml_text, output_folder, provider, language, font, i, transcribe, transfile):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.types.SynthesisInput(ssml = ssml_text)
    if font.split("_")[1] == "MALE":
        voice = texttospeech.types.VoiceSelectionParams(
            language_code = language,
            name = f'{language}-{font.split("_")[0]}',
            ssml_gender = texttospeech.enums.SsmlVoiceGender.MALE)
    elif font.split("_")[1] == "FEMALE":
        voice = texttospeech.types.VoiceSelectionParams(
            language_code = language,
            name = f'{language}-{font.split("_")[0]}',
            ssml_gender = texttospeech.enums.SsmlVoiceGender.FEMALE)
    else:
        logging.warning(f'[ERROR] - Gender {font.split("_")[1]} not available.')
    # Selects the type of audio file to return
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding = texttospeech.enums.AudioEncoding.LINEAR16)
    # Performs the text-to-speech request on the text input with the selected voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    # Writes the synthetic audio to the output file. The response's audio_content is binary.
    fname = he.getFilename('generated/', output_folder, provider, language, font, i, 'wav')   
    try:
        with open(fname, 'wb') as out:
            out.write(response.audio_content)
            out.close()
        logging.info(f"[INFO] - File {fname} written.")
        if transcribe:
            transfile.write(f"{os.path.basename(fname)}\t{he.removeTags(ssml_text)}\n")
            logging.info("[INFO] - Transcription written to file.")
    except Exception as e:
        logging.error(f'[ERROR] - File {fname} could not be written -> {e}.')
    return os.path.basename(fname)

# POLLY / AMAZON
def amazonTTS(text, aws_key, aws_secret, region, output_folder, provider, language, font, i, transcribe, transfile):
    texttype = "ssml" if "<" in text else "text"
    polly_client = boto3.Session(
        aws_access_key_id = aws_key,          
        aws_secret_access_key = aws_secret, 
        region_name = region).client('polly') # 'eu-central-1'
    response = polly_client.synthesize_speech(VoiceId = font, # Hans, Marlene or Vicki
        Engine = 'standard', 
        LanguageCode = language,
        OutputFormat = 'mp3',
        TextType = texttype,
        Text = text)
    fname = he.getFilename('generated/', output_folder, provider, language, font, i, 'mp3')
    try: 
        with open(fname, 'wb') as out:
            out.write(response['AudioStream'].read())
            out.close()
        logging.info(f"[INFO] - File {fname} written.")
        if transcribe:
            transfile.write(f"{os.path.basename(fname)}\t{he.removeTags(text)}\n")
            logging.info("[INFO] - Transcription written to file.")
        return os.path.basename(fname)
    except Exception as e:
        logging.error(f'[ERROR] - File {fname} could not be written -> {e}.')