''' TTS SERVICE USING MICROSOFT API '''
''' tiwalz@microsoft.com '''

# Import required packages
import requests
import logging
import uuid
import time
import re
import os
import pandas as pd
from datetime import datetime
from pydub import AudioSegment
from scipy.signal import lfilter, butter
from scipy.io.wavfile import read, write
from numpy import array, int16
import params as pa

# Load and set configuration parameters
pa.get_config()

''' MICROSOFT SPEECH API '''
class TextToSpeech(object):
    def __init__(self, subscription_key, language, font, region, text):
        self.subscription_key = subscription_key
        self.tts = f'<speak version="1.0" xml:lang="en-us"><voice xml:lang="{language}" name="Microsoft Server Speech Text to Speech Voice ({language}, {font})">{text}</voice></speak>'
        self.timestr = time.strftime("%Y%m%d-%H%M")
        self.access_token = None

    def get_token(self, region, subscription_key):
        """Get connection token to text to speech service
        Args:
            region: Name of the Azure region
            subscription_key: Key of Azure resource
        Returns:
            self.access_token: Sets access token gathered from the API
        """
        fetch_token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def save_audio(self, region, resource_name, output_directory, language, font):
        """Save generated audio to file
        Args:
            region: Name of the Azure region
            resource_name: Name of the Azure resource
            output_directory: Output directory for the file
            language: Language code of the synthetization language, e.g. en-US
            font: Name of the font, see documentation
        Returns:
            Saves audio to file
        """
        base_url = f'https://{region}.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': resource_name
        }
        response = requests.post(constructed_url, headers=headers, data=self.tts)
        if response.status_code == 200:
            fname = f"{output_directory}/tts_generated/{datetime.today().strftime('%Y-%m-%d')}_{language}_{font}_{str(uuid.uuid4().hex)}.wav"
            with open(fname, "wb") as audio:
                audio.write(response.content)
            return os.path.basename(fname)
        else:
            logging.error(f"[ERROR] - Status code: {str(response.status_code)} -> something went wrong, please check your subscription key and headers.")

''' PRE AND POSTPROCESS '''
# Remove XML/SSML Tags
def remove_tags(text):
    """Remove SSML tags from text strings
    Args:
        text: Raw text with SSML tags
    Returns:
        text_cleaned: Text without SSML tags
    """
    return re.compile(r'<[^>]+>').sub('', text)

def convert_to_custom_speech(output_directory, fname, rate, crop_start, crop_end):
    """Convert to Microsoft Speech Service format
    Args:
        output_directory: Output directory for the file
        fname: Filename for output file
        rate: Frame rate
        crop_start: Start of the audio file
        crop_end: End of the audio file
    Returns:
        Writes audio stream to file
    """
    # Check if it's Windows for driver import
    if os.name == "nt":
        AudioSegment.ffmpeg = pa.driver
        logging.debug("Running on Windows")
    else:
        logging.debug("Running on Linux")
    rec = AudioSegment.from_wav(f"{output_directory}/tts_generated/{fname}").set_frame_rate(rate).set_sample_width(2)
    rec = rec.set_channels(1)
    rec = rec[crop_start:crop_end]
    file_converted = f"{output_directory}/tts_converted/{fname}"
    rec.export(file_converted, format="wav", bitrate="192k")
    del rec

def bandpass_params(low_freq, high_freq, sample_rate, order=5):
    """Set bandpass params
    Args:
        low_freq: Low frequency value
        high_freq: High frequency value
        sample_rate: Sample rate of audio
        order: Order of the filter
    Returns:
        numerator: Fraction of audio 1
        denominator: Fraction of audio 2
    """
    nyq = 0.5 * sample_rate
    low = low_freq / nyq
    high = high_freq / nyq
    numerator, denominator = butter(order, [low, high], btype='band')
    return numerator, denominator

def bandpass_filter(audio, low_freq, high_freq, sample_rate, order=5):
    """Apply bandpass filter on the generated training data
    Args:
        audio: Audio file as object
        low_freq: Low frequency value
        high_freq: High frequency value
        sample_rate: Sample rate of audio
        order: Order of the filter
    Returns:
        filtered_audio: Filtered audio object
    """
    numerator, denominator = bandpass_params(low_freq, high_freq, sample_rate, order=order)
    filtered_audio = lfilter(numerator, denominator, audio)
    return filtered_audio

def convert_with_telephone_filter(output_directory, fname):
    """Apply telephone-like filter on the generated training data
    Args:
        output_directory: Output directory for the file
        fname: Filename of audio file
    Returns:
        Writes output to file
    """
    fs, audio = read(f"{output_directory}/tts_converted/{fname}")
    low_freq = 300.0
    high_freq = 3000.0
    filtered_signal = bandpass_filter(audio, low_freq, high_freq, fs, order=6)
    fname = f'{output_directory}/tts_telephone/{fname}'
    write(fname, fs, array(filtered_signal, dtype=int16))

def main(df, output_directory, custom=True, telephone=True):
    """Apply telephone-like filter on the generated training data
    Args:
        df: Data frame with utterances to be synthesized
        output_directory: Output directory for the file
        custom: Boolean to activate audio conversion to Microsoft Speech format
        telephone: Boolean to activate telephone filter in audio files
    Returns:
        df: Data frame with utterances and the file name of the synthesized audio file
    Raises:
        Exception: If TTS-request failed
    """
    os.makedirs(f'{output_directory}/tts_generated/', exist_ok=True)
    audio_synth = []
    for index, row in df.iterrows():
        try:
            app = TextToSpeech(pa.tts_key, pa.tts_language, pa.tts_font, pa.tts_region, row['text'])
            app.get_token(pa.tts_region, pa.tts_key)
            fname = app.save_audio(pa.tts_region, pa.tts_resource_name, output_directory, pa.tts_language, pa.tts_font)
            if custom:
                os.makedirs(f'{output_directory}/tts_converted/', exist_ok=True)
                convert_to_custom_speech(output_directory, fname, 8000, 0, None)
            if telephone:
                os.makedirs(f'{output_directory}/tts_telephone/', exist_ok=True)
                convert_with_telephone_filter(output_directory, fname)          
            logging.info(f'[INFO] - Synthesized {fname}')
        except Exception as e:
            logging.error(f'[ERROR] - Synthetization of "{row["text"]}" failed -> {e}')
            fname = "nan"
        audio_synth.append(fname)
    df['audio_synth'] = audio_synth
    df['text_ssml'] = df['text'].copy()
    df['text'] = df['text_ssml'].apply(remove_tags)
    return df

if __name__ == '__main__':
    main(pd.DataFrame({'text': ['This is a test', 'And this is another test!']}), "output/test")