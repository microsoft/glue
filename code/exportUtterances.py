''' EXPORT ENDPOINT UTTERANCES '''
''' tiwalz@microsoft.com '''
import http.client, urllib.request, urllib.parse, urllib.error, base64, json, io, csv
import pandas as pd
import logging
import argparse
from datetime import datetime

''' COMMAND EXAMPLES '''
# python .\code\exportUtterances.py  --key [subscription-key] --appid [app-id]

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--key",
                type=str,
                help="Pass subscription key")  
parser.add_argument("--appid",
                type=str,
                help="Pass appid")  
args = parser.parse_args()
subscription_key = args.key
appid = args.appid

headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
}
params = urllib.parse.urlencode({
    'includeResponse': 'true',
})

try:
    conn = http.client.HTTPSConnection('cs-ba-vb-we-d-luisauthoring.cognitiveservices.azure.com')
    conn.request("GET", f"/luis/authoring/v3.0-preview/apps/{appid}/querylogs/?%s" % params, '{body}', headers)
    response = conn.getresponse()
    data = response.read()
    pd.read_csv(io.BytesIO(data), encoding="utf-8").to_csv(f'{datetime.today().strftime("%Y-%m-%d")}-export.csv', sep="\t", encoding="utf-8")
    logging.warning('[SUCCESS] - Endpoint utterances written to output file.')
    conn.close()
except Exception as e:
    print(f"[Errno {e.errno}] {e.strerror}")