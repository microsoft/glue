''' TTS SERVICE USING MICROSOFT API '''
''' tiwalz@microsoft.com '''

# Import required packages
import requests
import random
import logging
import uuid
import time
import sys
import re
import os
import configparser
from datetime import datetime
from pydub import AudioSegment
from scipy.signal import lfilter, butter
from scipy.io.wavfile import read, write
from numpy import array, int16

# Get config file
sys.path.append('./')
config = configparser.ConfigParser()
try:
    config.read('config.ini')
    AudioSegment.converter = config['driver']['path']
except Exception as e:
    logging.error(f'[ERROR] - {e}')

''' MICROSOFT SPEECH API '''
class TextToSpeech(object):
    def __init__(self, subscription_key, language, font, region, text):
        self.subscription_key = subscription_key
        self.tts = f'<speak version="1.0" xml:lang="en-us"><voice xml:lang="{language}" name="Microsoft Server Speech Text to Speech Voice ({language}, {font})">{text}</voice></speak>'
        self.timestr = time.strftime("%Y%m%d-%H%M")
        self.access_token = None

    def get_token(self, region, subscription_key):
        '''
        Get connection token to text to speech service
        '''
        fetch_token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def save_audio(self, region, resource_name, output_folder, case, language, font):
        '''
        Save generated audio to file
        '''
        base_url = f'https://{region}.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': resource_name
        }
        response = requests.post(constructed_url, headers=headers, data=self.tts)
        if response.status_code == 200:
            fname = f"{output_folder}{case}generated/{datetime.today().strftime('%Y-%m-%d')}_{language}_{font}_{random.randint(10000,99999)}.wav"
            with open(fname, "wb") as audio:
                audio.write(response.content)
            return os.path.basename(fname)
        else:
            sys.exit(f"[ERROR] - Status code: {str(response.status_code)} -> something went wrong, please check your subscription key and headers.")

def batch_synthesize(df, subscription_key, language, font, region, resource_name, output_folder, case, custom=True, tel=True):
    """Synthesize text snippets to audio files
    Args:
        param1: 
        param2: 
    Returns:
        The return value. 
    """
    os.makedirs(f'{output_folder}{case}generated/', exist_ok=True)
    audio_synth = []
    for index, row in df.iterrows():
        try:
            app = TextToSpeech(subscription_key, language, font, region, row['text'])
            app.get_token(region, subscription_key)
            fname = app.save_audio(region, resource_name, output_folder, case, language, font)
            if custom:
                os.makedirs(f'{output_folder}{case}converted/', exist_ok=True)
                custom_speech(output_folder, case, fname, 8000, 0, None)
            if tel:
                os.makedirs(f'{output_folder}{case}noise/', exist_ok=True)
                telephone_filter(output_folder, case, fname)          
            logging.warning(f'[INFO] - Synthesized {fname}')
        except Exception as e:
            logging.warning(f'[ERROR] - Synthetization of {row["text"]} failed -> {e}')
            fname = "nan"
        audio_synth.append(fname)
    df['audio_synth'] = audio_synth
    return df

''' PRE AND POSTPROCESS '''
# Remove XML/SSML Tags
def remove_tags(text):
    '''
    Remove SSML tags from text strings
    '''
    return re.compile(r'<[^>]+>').sub('', text)

def custom_speech(output_folder, case, fname, rate, crop_start, crop_end):
    '''
    Convert to Microsoft Speech Service format
    '''
    rec = AudioSegment.from_wav(f"{output_folder}{case}generated/{fname}").set_frame_rate(rate).set_sample_width(2)
    rec = rec.set_channels(1)
    rec = rec[crop_start:crop_end]
    file_converted = f"{output_folder}{case}converted/{fname}"
    rec.export(file_converted, 
                format="wav",
                bitrate="192k")
    del rec

def bandpass_params(low_freq, high_freq, fs, order=5):
    '''
    Set bandpass params
    '''
    nyq = 0.5 * fs
    low = low_freq / nyq
    high = high_freq / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, low_freq, high_freq, fs, order=5):
    '''
    Apply bandpass filter on the generated training data
    '''
    b, a = bandpass_params(low_freq, high_freq, fs, order=order)
    y = lfilter(b, a, data)
    return y

def telephone_filter(output_folder, case, fname):
    '''
    Apply telephone-like filter on the generated training data
    '''
    fs,audio = read(f"{output_folder}{case}converted/{fname}")
    low_freq = 300.0
    high_freq = 3000.0
    filtered_signal = bandpass_filter(audio, low_freq, high_freq, fs, order=6)
    fname = f'{output_folder}{case}noise/{fname}'
    write(fname, fs, array(filtered_signal, dtype=int16))

def main():
    return None

if __name__ == '__main__':
    main()