import TextToSpeech as tts
import pandas as pd
import os

def test_tts_main():
    df = tts.generate_tts(pd.DataFrame({'text': ['This is a test', 'And this is another test!']}), "output/test")
    assert list(df) == ['text', 'audio_synth', 'text_ssml']
    for index, row in df.iterrows():
        assert os.path.isfile(f"output/test/tts_telephone/{row['audio_synth']}")