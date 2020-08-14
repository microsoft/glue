''' HELPER FUNCTIONS '''
import os
import re
import glob
import datetime
import time
import logging
import sys
from azure.storage.blob import BlockBlobService

# Import sub scripts
try:
    from __app__ import audio as au
    from __app__ import services as se
except Exception as e:
    sys.path.append('./')
    import AudioBatchFunc.audio as au
    import AudioBatchFunc.services as se

''' CASE MANAGEMENT '''
# Get output folder
def createCase(dir_path, provider, language, level, job_id):
    case = f"{job_id}/"
    output_folder = f"{dir_path}/{case}"
    logging.info(f'[INFO] - Initiating case creation, level {level}.')
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            os.makedirs(f'{output_folder}/generated/')
            logging.info(f'[INFO] - Created case folder {case}.')
        if not os.path.exists(f'{output_folder}/converted/') and int(level)>=1: 
            os.makedirs(f'{output_folder}/converted/')
            logging.info(f'[INFO] - Created case folder {case} -> level >= 1.')
        if not os.path.exists(f'{output_folder}/noise/') and int(level)==2: 
            os.makedirs(f'{output_folder}/noise/')
            logging.info(f'[INFO] - Created case folder {case} -> level >= 2.')
        logging.info(f'[INFO] - Created case {case} or re-opened existing one.')
    except Exception as e:
        logging.error(f'[ERROR] - Error at creating or opening case -> {e}.')
    return output_folder, case

# Get filename
def getFilename(mode, output_folder, provider, language, font, i, format):
    filename = f"{output_folder}{mode}{datetime.datetime.today().strftime('%Y-%m-%d')}_{provider}_{language}_{font}_{str(i)}.{format}"
    logging.info(f'[INFO] - Created filename {filename}.')
    return filename

''' PREPROCESS '''
# Remove XML/SSML Tags
def removeTags(text):
    logging.info(f'[INFO] - Removing SSML-tags from input text.')
    text = re.compile(r'<[^>]+>').sub('', text)
    text = ' '.join(text.split())
    return text

def copytoBLOB(local_file_path, fname, blobstring, container):
    try:
        # Create a blob client using the local file name as the name for the blob
        logging.info(f"[INFO] - Initiating upload to BLOB-storage.")
        blob_service_client = BlockBlobService(connection_string=blobstring)
        logging.info(f'[INFO] - Built connection to BLOB storage.')
        for path, subdirs, files in os.walk(local_file_path):
            files = [k for k in files if fname in k or k.endswith(".txt") or k == f'{os.path.splitext(fname)[0]}.wav']
            for name in files:
                path_full = os.path.join(path, name)
                path_blob = os.path.join(path, name).replace("/tmp/", "")
                logging.info(f"[INFO] - Uploading to Azure Storage as BLOB: {path_full}.")
                blob_service_client.create_blob_from_path(container, path_blob, path_full)
        logging.info(f'[INFO] - Successfully uploaded to BLOB.')
    except Exception as e:
        logging.error(f"[ERROR] - Copy to BLOB failed -> {e}.")

def cleanUp(dir_path, output_folder):
    logging.warning(f'[WARNING] - Deleting audio files from Azure Function temp storage.')
    for path, subdirs, files in os.walk(output_folder):
        for name in files:
            if name.endswith(('.MP3', '.mp3', '.wav', '.WAV')):
                try:
                    os.remove(os.path.join(path, name))
                    logging.warning(f'[INFO] - Deleted {os.path.join(path, name)}.')
                except Exception as e:
                    logging.error(f'[ERROR] - Could not delete {os.path.join(path, name)}.')
                    continue
    """
    logging.warning(f'[WARNING] - Deleting cases older than two days.')
    for path, subdirs, files in os.walk(dir_path):
        for sub in subdirs:
            timestamp = os.path.getmtime(os.path.join(path, sub))
            if time.time() - 86400 * 2 > timestamp:
                try:
                    # os.remove(os.path.join(path, sub))
                    logging.warning(f'[INFO] - Deleted {sub}.')
                except Exception as e:
                    logging.error(f'[ERROR] - Could not delete {os.path.join(path, sub)} -> {e}.')
                    continue
    """

def writeError(output_folder, text, exception):
    newline = "\n"
    errorfile = open(f'{output_folder}errors.txt', 'a')
    errorfile.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}\t{text}\t{str(exception).replace(newline, " ")}\n')
    errorfile.close()
    logging.warning(f"[WARNING] - Wrote failed utterance to error logfile -> {exception}.")