import pytest
import sys
sys.path.append("./src")
import tts

def generate_tts(df, output):
    df = tts.main(df, output)
    return df