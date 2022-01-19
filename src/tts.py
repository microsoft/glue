''' TTS SERVICE USING MICROSOFT API '''
''' nonstoptimm@gmail.com '''

# Import required packages
import logging
import uuid
import re
import os
import pandas as pd
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig

from datetime import datetime
from pydub import AudioSegment
from scipy.signal import lfilter, butter
from scipy.io.wavfile import read, write
from numpy import array, int16
import params as pa

# Load and set configuration parameters
pa.get_config()

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

def get_ssml_string(text, language, font):
    """Pack text into a SSML document
    Args:
        text: Raw text with SSML tags
        language: Language-code, e.g. de-DE
        font: TTS font, such as KatjaNeural
    Returns:
        ssml: String as SSML XML notation
    """
    ssml = f'<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="en-US"><voice name="{language}-{font}">{text}</voice></speak>'
    return ssml

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
    try:
        rec = AudioSegment.from_wav(f"{output_directory}/tts_generated/{fname}").set_frame_rate(rate).set_sample_width(2)
        rec = rec.set_channels(1)
        rec = rec[crop_start:crop_end]
        file_converted = f"{output_directory}/tts_converted/{fname}"
        rec.export(file_converted, format="wav", bitrate="192k")
        del rec
    except Exception as e:
        logging.error(f'[ERROR] - Failed applying telephone filter for {fname} -> {e}')

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
    try:
        fs, audio = read(f"{output_directory}/tts_converted/{fname}")
        low_freq = 300.0
        high_freq = 3000.0
        filtered_signal = bandpass_filter(audio, low_freq, high_freq, fs, order=6)
        fname = f'{output_directory}/tts_telephone/{fname}'
        write(fname, fs, array(filtered_signal, dtype=int16))
    except Exception as e:
        logging.error(f'[ERROR] - Failed applying telephone filter for {fname} -> {e}')

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
        Exception: If tts-request failed
    """
    # Check if it's Windows for driver import - if not, setting of driver is not necessary
    if os.name == "nt":
        AudioSegment.ffmpeg = pa.config_data['driver']
        logging.debug("Running on Windows")
    else:
        logging.debug("Running on Linux")
    # Create output folder for TTS generation
    os.makedirs(f'{output_directory}/tts_generated/', exist_ok=True)
    audio_synth = []
    # Instantiate SpeechConfig for the entire run, as well as voice name and audio format
    speech_config = SpeechConfig(subscription=pa.config_data['tts_key'], region=pa.config_data['tts_region'])
    speech_config.speech_synthesis_voice_name = f'{pa.config_data["tts_language"]}-{pa.config_data["tts_font"]}'
    speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat['Riff24Khz16BitMonoPcm'])
    # Loop through dataframe of utterances
    for index, row in df.iterrows():
        # Submit request to TTS
        try:
            fname = f"{datetime.today().strftime('%Y-%m-%d')}_{pa.config_data['tts_language']}_{pa.config_data['tts_font']}_{str(uuid.uuid4().hex)}.wav"
            # AudioOutputConfig has to be set separately due to the file names
            audio_config = AudioOutputConfig(filename=f'{output_directory}/tts_generated/{fname}')
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            # Submit request and write outputs
            synthesizer.speak_ssml_async(get_ssml_string(row['text'], pa.config_data['tts_language'], pa.config_data['tts_font']))
        except Exception as e:
            logging.error(f'[ERROR] - Synthetization of "{row["text"]}" failed -> {e}')
            audio_synth.append('nan')
            continue
        else:
            audio_synth.append(fname)
        # Convert to Microsoft Speech format, if desired
        if custom:
            os.makedirs(f'{output_directory}/tts_converted/', exist_ok=True)
            convert_to_custom_speech(output_directory, fname, 8000, 0, None)
        # Apply telephone filter and write to new file, if desired
        if telephone:
            os.makedirs(f'{output_directory}/tts_telephone/', exist_ok=True)
            convert_with_telephone_filter(output_directory, fname)          
        logging.info(f'[INFO] - Synthesized file {str(index+1)}/{str(len(df))} - {fname}')
        
    # Set output lists to data frame
    df['audio_synth'] = audio_synth
    df['text_ssml'] = df['text'].copy()
    df['text'] = df['text_ssml'].apply(remove_tags)
    return df

if __name__ == '__main__':
    main(pd.DataFrame({'text': ['Ich möchte testen, ob die API auch Umlaute kann.', 'This is a test.', 'And this is another <say-as interpret-as="characters">test</say-as>!']}), "output/test")