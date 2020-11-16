''' LUIS SCORING SCRIPT '''
''' tiwalz@microsoft.com '''

# Import required packages
import logging
import requests
import json
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import pandas as pd
import sys
from datetime import datetime
import argparse
import shutil
import os
import configparser
import time

# Define scoring function
def score_endpoint(df, mode, app_id, endpoint, key, tres, slot='production'):
    """Scores or loads a LUIS scoring file to assess the model quality and delivers insights
    Args:
        df: input data frame
        mode: choice between scoring and 
        appId: LUIS app ID
        key: LUIS subscription key
        tres: minimum confidence score for LUIS result, between 0.00 and 1.00
    Returns:
        df: scoring data frame with predicted intents and scores
    Raises:
      ConnectionError: if file is not found
    """
    predictions = []
    scores = []
    drops = []
    logging.info(f'[START] - STARTED LUIS MODEL SCORING of {len(df)} utterances ... ')
    for index, row in df.iterrows():
        try:
            # Uncomment this if you are using the old url version having the region name as endpoint
            # endpoint_url = f'{endpoint}.api.cognitive.microsoft.com'
            # Below, you see the most current version of the api having the prediction resource name as endpoint
            endpoint_url = f'{endpoint}.cognitiveservices.azure.com'
            headers = {}
            params = {
                'query': row['text'],
                'timezoneOffset': '0',
                'verbose': 'true',
                'show-all-intents': 'true',
                'spellCheck': 'false',
                'staging': 'false',
                'subscription-key': key
            }
            r = requests.get(f'https://{endpoint_url}/luis/prediction/v3.0/apps/{app_id}/slots/{slot}/predict', headers=headers, params=params)
            # Check
            if mode == "json":
                parsed = json.loads(r.text)
                print(json.dumps(parsed, indent=2))
            elif mode == "score":
                data = r.json()
                topIntent = data['prediction']['topIntent']
                topScore = data['prediction']['intents'][topIntent]['score']
                # TODO - second and third best confidence
                if topScore < tres: 
                    drop = "None"
                else:
                    drop = topIntent
                logging.info(f"[INFO] {str(index+1)}/{len(df)} -> '{row['text']}' -> Original: {row['intent']}, Pred: {topIntent} ({topScore}, drop? {topIntent != row['intent']})")
            predictions.append(topIntent)
            scores.append(topScore)
            drops.append(drop)
        except Exception as e:
            logging.error(f'[INFO] - {e}')
            predictions.append("nan")
            scores.append("nan")
            drops.append("nan")
    if mode == "score":
        df['prediction'] = predictions
        df['score'] = scores
        df['drop'] = drops
    return df

def main():
    return None

if __name__ == '__main__':
    main()