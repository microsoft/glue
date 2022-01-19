''' LUIS SCORING SCRIPT '''
''' nonstoptimm@gmail.com '''

# Import standard packages
import logging
import requests
import json
import pandas as pd
import time
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

# Import custom modules
import params as pa

# Load and set configuration parameters
pa.get_config()

def request_luis(text):
    """Scores or loads a LUIS scoring file to assess the model quality and delivers insights
    Args:
        text: Text string for LUIS request
    Returns:
        r.json: Response from endpoint as JSON
    """
    # Uncomment this if you are using the old url version having the region name as endpoint.
    # endpoint_url = f'{endpoint}.api.cognitive.microsoft.com'.
    # Below, you see the most current version of the api having the prediction resource name as endpoint.     
    endpoint_url = f'{pa.config_data["luis_endpoint"]}.cognitiveservices.azure.com'
    headers = {}
    params = {
        'query': text,
        'timezoneOffset': '0',
        'verbose': 'true',
        'show-all-intents': 'true',
        'spellCheck': 'false',
        'staging': 'false',
        'subscription-key': pa.config_data['luis_key']
    }
    r = requests.get(f'https://{endpoint_url}/luis/prediction/v3.0/apps/{pa.config_data["luis_appid"]}/slots/{pa.config_data["luis_slot"]}/predict', headers=headers, params=params)
    # Check
    logging.debug(json.dumps(json.loads(r.text), indent=2))
    return r.json()

def luis_classification_report(df, col):
    """Creates LUIS classification report and confusion matrix
    Args:
        df: A data frame with ground truth and predictions
        col: Name of column of prediction
    Returns:
        Output to console as logging
    """
    logging.info('[INFO] - Starting to create classification report')
    logging.info('[OUTPUT] - CLASSIFICATION REPORT (without reset by treshold):')
    logging.info(classification_report(df['intent'], df[f'prediction_{col}']))
    logging.info(f'[OUTPUT] - AFTER RESET BY TRESHOLD ({pa.config_data["luis_treshold"]}):')
    logging.info(classification_report(df['intent'], df[f'prediction_drop_{col}']))
    logging.info('[OUTPUT] - CONFUSION MATRIX:')
    logging.info(f'\n{confusion_matrix(df["intent"], df[f"prediction_{col}"])}')

def main(df, col):
    """Main function of the LUIS scoring component.
    Args:
        df: Data frame with ground truth and predictions
        col: Name of column of prediction
    Returns:
        df: Data frame with appended predictions
    """
    # Set lists for results
    predictions = []
    scores = []
    prediction_drop = []
    # Loop through text rows, predict and process values
    for index, row in df.iterrows():
        try:
            # Send LUIS request
            data = request_luis(row[col])
            # Extract relevant information from results
            top_intent = data['prediction']['topIntent']
            top_score = data['prediction']['intents'][top_intent]['score']
            # Evaluate scores based on treshold and set None-intent if confidence is too low
            if top_score < pa.config_data['luis_treshold']: 
                drop = "None"
            else:
                drop = top_intent
            logging.info(f"[INFO] {str(index+1)}/{len(df)} -> '{row[col]}' -> Original: {row['intent']}, Pred: {top_intent} ({top_score}, drop? {top_intent != row['intent']})")
            # Append scores and predictions to lists
            predictions.append(top_intent)
            scores.append(top_score)
            prediction_drop.append(drop)
            # Go to sleep for half a second to avoid excess requests
            # You may disable this if your quota is sufficient
            time.sleep(0.5)
        except Exception as e:
            logging.error(f'[ERROR] - Request failed -> {e}')
            predictions.append("nan")
            scores.append("nan")
            prediction_drop.append("nan")
    # Append lists as columns to data frame
    df[f'prediction_{col}'] = predictions
    df[f'score_{col}'] = scores
    df[f'prediction_drop_{col}'] = prediction_drop
    # Create and print classification report
    luis_classification_report(df, col)
    return df

if __name__ == '__main__':
    df = main(pd.DataFrame({'intent': ['Book_Flight', 'Cancel_Flight'], 'text': ['I want to book a flight to Singapore.', 'I need to cancel my flight from Stuttgart to Singapore.']}))
    print(df)