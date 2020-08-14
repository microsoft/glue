''' AUDIO DATA GENERATION FUNCTION '''
''' tiwalz@microsoft.com '''
# Import packages
import azure.functions as func
import re
import sys
import os
import requests
import shutil
import glob
import logging
import random
import json
import tempfile
import time
import datetime

# Import sub scripts
try:
    from __app__ import helper as he
    from __app__ import audio as au
    from __app__ import services as se
    from __app__ import params as pa
except Exception as e:
    logging.warning('[INFO] - Main: Using local imports.')
    sys.path.append('C:\\Users\\tiwalz\\Documents\\Projects\\Daimler\\iBDC_VoiceBot_CPL_DataScience\\code\\CPL\\')
    import AudioBatchFunc.helper as he
    import AudioBatchFunc.audio as au
    import AudioBatchFunc.services as se
    import AudioBatchFunc.params as pa

''' REQUEST EXECUTION '''
def main(req: func.HttpRequest) -> func.HttpResponse:
    # Main try
    try:
        logging.info('[INFO] - Python HTTP trigger function processed a request.')
        # Collect parameters
        if req.get_body():
            data = json.loads(req.get_body())[0]
            logging.info(f'[INFO] - Received data from request body.')
        else:
            data = req.params
            logging.info(f'[WARNING] - Received data as request params.')

        # Get parameters
        pa.getParams(data)
        
        # Simple statement to check whether text is empty
        if pa.text is None:
            raise TypeError("'None' value provided as input text.")

        # Create case
        output_folder, case = he.createCase(pa.dir_path, pa.provider, pa.language, pa.level, pa.job_id)

        # If transcribe-variable is True, a transcription file will be written. Otherwise it is just skipped.
        if pa.transcribe:
            transfile = open(f"{output_folder}{pa.job_id}_transcriptions.txt", "a")
            transfile.write('\ufeff')
            logging.info(f'[INFO] - Opened transcription file with UTF-8 BOM encoding.')
        else:
            transfile = "" 

        # Synthesize request
        logging.info(f'[INFO] - Synthesizing: "{pa.text}".')
        try:
            if pa.provider == "Microsoft":
                app = se.TextToSpeech(pa.subscription_key, pa.language, pa.font, pa.text, pa.region)
                app.get_token(pa.region, pa.subscription_key)
                fname = app.save_audio(pa.region, pa.resource_name, output_folder, pa.provider, pa.language, pa.font, datetime.datetime.now().strftime("%f"), pa.transcribe, transfile)
            elif pa.provider == "Google":
                fname = se.googleTTS(pa.text, output_folder, pa.provider, pa.language, pa.font, datetime.datetime.now().strftime("%f"), pa.transcribe, transfile)
                os.remove(f"{pa.dir_path}/auth.json") if os.path.exists(f"{pa.dir_path}/auth.json") else f"[INFO] - No {pa.provider} auth file found, nothing to delete."
            elif pa.provider == "Amazon":
                fname = se.amazonTTS(pa.text, pa.aws_key, pa.aws_secret, pa.aws_region, output_folder, pa.provider, pa.language, pa.font, datetime.datetime.now().strftime("%f"), pa.transcribe, transfile)
            else:
                raise TypeError(f'[ERROR] - Service "{pa.provider}" is not supported, please choose "Microsoft", "Google" or "Amazon".')
        except Exception as e:
            logging.warning(f'[ERROR] - Request on service "{pa.provider}" failed -> {e}.')
            he.writeError(output_folder, pa.text, e)
            raise TypeError(f'Failed to build up connection with {pa.provider}.')

        ''' FILE HANDLING '''
        # Convert to MP3
        if "mp3" in fname:
            au.convertMP3(output_folder, fname)
        else:
            logging.info(f'[INFO] - No mp3 files found, skipping conversion.')

        # Convert to Custom Speech format
        try:
            if int(pa.level) == 1:
                au.customSpeech(output_folder, fname, 8000, 0, None)
            elif int(pa.level) == 2:
                au.customSpeech(output_folder, fname, 8000, 0, None)
                au.telephoneFilter(output_folder, fname)
        except Exception as e:
            logging.warning(f'[ERROR] -> Failed to convert audio files -> {e}.')

        # Close transcription file
        if pa.transcribe: 
            transfile.close()
            # Copy files to subfolders
            [shutil.copy(f"{output_folder}{pa.job_id}_transcriptions.txt", f'{directory}/transcriptions.txt') for directory, x, y in os.walk(f'{output_folder}')]
            # Remove initial file
            os.remove(f'{output_folder}transcriptions.txt')

        # Copy file to BLOB
        he.copytoBLOB(output_folder, fname, pa.blobstring, pa.container)

        # Delete old ones
        he.cleanUp(pa.dir_path, output_folder)

        ''' RESPONSE '''
        res = json.dumps(dict(
            job_id          =   pa.job_id,
            text            =   pa.text,
            transcription   =   he.removeTags(pa.text),
            service         =   pa.provider,
            code            =   200,
            output          =   [{"level": pa.level, "filename": fname, "transcribe": pa.transcribe}]
            )
        )
        ''' RESPONSE '''
        return func.HttpResponse(res, mimetype='application/json')
    except Exception as e:
        logging.error(f'[ERROR] -> {e}.')
        # Copy error-file
        he.copytoBLOB(output_folder, "errors.txt", pa.blobstring, pa.container)
        return func.HttpResponse(
             f"[ERROR] - Received errorneous request or invalid API data -> {e}",
             status_code=500
        )
    
    