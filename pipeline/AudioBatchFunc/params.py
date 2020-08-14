''' PARAMETERS COLLECTOR '''
import os
import sys
import tempfile
import logging
import html

def getParams(req):
    logging.info(f'[INFO] - Collecting input parameters.')
    global dir_path, language, provider, font, text, output_format, transcribe, level, job_id, blobstring, container, region, resource_name, subscription_key, aws_key, aws_secret, aws_region 
    # Get temporary dir
    dir_path = tempfile.gettempdir()
    # General parameters
    language = req.get('lang')
    provider = req.get('provider')
    font = req.get('font')
    text = html.unescape(req.get('input'))
    output_format = req.get('format')
    # Case management
    transcribe = True if req.get('transcribe') == "True" or req.get('transcribe') == "true" else False
    level = req.get('level')
    job_id = req.get('jobid') 
    # General Resources
    blobstring = os.environ.get('AZURE_BLOB')
    container = os.environ.get('AZURE_BLOB_CONTAINER')
    # Microsoft Cognitive Services
    region = os.environ.get('COGNITIVE_REGION')
    resource_name = os.environ.get('COGNITIVE_NAME')
    subscription_key = os.environ.get('COGNITIVE_KEY')
    # AWS
    aws_key = os.environ.get('AWS_ACCESS')
    aws_secret = os.environ.get('AWS_ACCESS_SECRET')
    aws_region = os.environ.get('AWS_REGION')
    # Google Service
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_STORE'):
        auth = open(f"{dir_path}/auth.json", "w+")
        auth.write(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_STORE'))
        auth.close()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{dir_path}/auth.json"
    # Load BLOB keys
    if blobstring is None:
        # Local debugging
        sys.path.append('./')
        import configparser
        config = configparser.ConfigParser()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'auth.json'
        config.read('config.ini')
        blobstring = config['blobstring']['string']
        container = config['blobstring']['container']
        subscription_key = config['cognitive']['key']
        region = config['cognitive']['region']
        resource_name = config['cognitive']['name']
        aws_key = config['aws']['key']
        aws_secret = config['aws']['secret']
        aws_region = config['aws']['region']