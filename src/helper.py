''' HELPER FUNCTIONS ACROSS MULTIPLE SCRIPTS '''
''' tiwalz@microsoft.com '''

# Import required packages
from datetime import datetime
import os
import argparse
import shutil
import glob
import codecs
import logging
import configparser
import pandas as pd
from sklearn.model_selection import train_test_split

# Helper Functions
def create_case(output_folder, subfolders):
    """ Create case for project
    Args:
        output_folder: directory of output folder
        subfolders: list of folders to be created as subfolders
    Returns:
        output_folder: directory of output folder
        case: name of the created case
        output_file: name of text output file
    """
    # Create Case
    case = f"{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}"
    output_file = f"{output_folder}/{case}/{datetime.today().strftime('%Y-%m-%d')}.txt"
    os.makedirs(f"{output_folder}/{case}", exist_ok=True)
    for folder in subfolders.split(","):
        os.makedirs(f"{output_folder}/{case}/{folder}", exist_ok=True)
    return output_folder, case, output_file

# General Function
#def write_transcription(output_folder, case, text):
#    ''' Write transcriptions '''
#    if not os.path.exists(f'{output_folder}{case}transcriptions.txt'):
#        transfile = codecs.open(f'{output_folder}{case}transcriptions.txt', 'w', encoding='utf-8-sig')
#        transfile.close()
#        logging.warning(f'[INFO] - Created transcript file with utf-8 bom encoding.')
#    with open(f"{output_folder}{case}transcriptions.txt", "a", encoding='utf-8-sig') as transfile:
#        transfile.write(f'{text}\n')
#        transfile.close()
#    #logging.info(f'[INFO] - Written to transcript file.')         

def unravel_xls(fname):
    df = pd.read_csv(fname, sep="\t", encoding="utf-8", index_col=None)
    df_new = pd.DataFrame(columns=['text', 'intent'])
    for index, row in df.iterrows():
        split_rows = row['text'].split('\r\n')
        #split_rows = ["- " + split for split in split_rows]
        new_row = pd.DataFrame({'text': split_rows, 'intent': row['intent']})
        df_new = df_new.append(new_row, ignore_index=True)
    #df_new.to_csv('file_unravel.txt', sep="\t", index=False)
    df_new = df_new[['intent', 'text']]
    df_new['text'] = df_new['text'].str.replace("- ", "").str.strip()
    return df_new

def create_df(fname):
    df = pd.DataFrame(columns=['intent', 'text'])
    intents = []
    texts = []
    with open(fname, encoding="utf-8") as lufile:
        line = lufile.readlines()
        current_intent = ""
        for l in line:
            l = l.replace("\n", "")
            if "##" in l:
                current_intent = l.replace('## ', '')
            elif current_intent != "":
                if "#" in l or l == "":
                    continue
                intents.append(current_intent)
                texts.append(l.replace("- ", ""))
            else:
                continue
        df = pd.DataFrame({'intent': intents, 'text': texts})
    #df.to_csv('out_df.txt', sep='\t', encoding='utf-8', index=None)
    return df

def write_lu(luis_file):
    luis_file = luis_file.sort_values(by=['intent', 'text'])
    file = open(f"../output/{datetime.today().strftime('%Y-%m-%d')}-luis.lu", "w")
    compare = ""
    for index, row in luis_file.iterrows():
        if len(row['intent']) < 4: continue
        if row['text'] == "": continue
        if compare != row['intent']:
            # Begin intent
            line = f"\n## {row['intent']}\n"
            file.writelines(line)
            line = f"- {str(row['text'])}\n"
            file.writelines(line.lower())
            compare = row['intent']
        else:
            line = f"- {str(row['text'])}\n"
            file.writelines(line.lower())
    file.close()

if __name__ == '__main__':
    #df_new = unravelXLS("input/2020-07-14-BotTesting-All.txt")
    #df = createDF('input/2020-07-07-luis.lu')
    # ArgumentParser
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                    type=str,
                    default="input/testset-example.txt",
                    help="give the whole path to tab-delimited file")  
    args = parser.parse_args()
    # Set arguments
    fname = args.input

    try:
        df = pd.read_csv(fname, sep="\t", encoding="utf-8")
        logging.info(f'[INFO] - imported data set')
        X_train, X_test = train_test_split(df, stratify=df['intent'], test_size=0.25)
        logging.info(f'[INFO] - successfully split data set')
        X_test.to_csv(f'input/{datetime.today().strftime("%Y-%m-%d")}-stratify-test.txt', sep='\t', encoding='utf-8')
        logging.warning(f'[SUCCESS] -> wrote split to input folder')
    except Exception as e:
        logging.warning(f'[ERROR] - splitting data set failed -> {e}')
    #writeLU(df_new)