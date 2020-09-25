''' AUDIO PROCESSING '''
import sys
import logging
import os
from pydub import AudioSegment
from scipy.signal import lfilter, butter
from scipy.io.wavfile import read, write
from numpy import array, int16
import tempfile

# Import sub scripts
try:
    from __app__ import helper as he
    from __app__ import service as se
except Exception as e:
    sys.path.append('./')
    import AudioBatchFunc.helper as he
    import AudioBatchFunc.services as se

def convertMP3(output_folder, fname):
    try:
        sound = AudioSegment.from_mp3(f'{output_folder}/generated/{fname}')
        sound.export(f"{output_folder}/generated/{os.path.splitext(os.path.basename(fname))[0]}.wav", format="wav")
        logging.info(f"[INFO] - Converting {fname} to wav.")
        return True
    except Exception as e:
        logging.error(f'[ERROR] - File conversion from mp3 to wav not successful -> {e}.')
        return False

def customSpeech(output_folder, fname, rate, crop_start, crop_end):
    try:
        logging.info(f'[INFO] - Converting {os.path.splitext(os.path.basename(fname))[0]}.wav to Microsoft Speech format.')
        rec = AudioSegment.from_wav(f"{output_folder}/generated/{os.path.splitext(os.path.basename(fname))[0]}.wav").set_frame_rate(rate).set_sample_width(2)
        rec = rec.set_channels(1)[crop_start:crop_end]
        file_converted = f"{output_folder}/converted/{os.path.splitext(os.path.basename(fname))[0]}.wav"
        rec.export(file_converted, format="wav", bitrate="192k")
        logging.info(f"[INFO] - Converted {os.path.splitext(os.path.basename(fname))[0]}.wav.")
        return True
    except Exception as e:
        logging.error(f'[ERROR] - File conversion not successful -> {e}.')
        return False

def butter_params(low_freq, high_freq, fs, order=5):
    nyq = 0.5 * fs
    low = low_freq / nyq
    high = high_freq / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, low_freq, high_freq, fs, order=5):
    b, a = butter_params(low_freq, high_freq, fs, order=order)
    y = lfilter(b, a, data)
    return y

def telephoneFilter(output_folder, fname):
    try:
        fs, audio = read(f"{output_folder}converted/{os.path.splitext(os.path.basename(fname))[0]}.wav")
        filtered_signal = butter_bandpass_filter(audio, 300.0, 3000.0, fs, order=6)
        fname = f'{output_folder}noise/{os.path.splitext(os.path.basename(fname))[0]}.wav'
        write(fname, fs, array(filtered_signal, dtype=int16))
        logging.info(f'[INFO] - Simulated telephone line for {fname}.')
        return True
    except Exception as e:
        logging.error(f'[ERROR] - File conversion not successful -> {e}.')
        return False