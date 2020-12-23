''' HELPER FUNCTIONS ACROSS MULTIPLE SCRIPTS '''
''' tiwalz@microsoft.com '''

# Import standard packages
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
    os.makedirs(f"{output_folder}/{case}", exist_ok=True)
    for folder in subfolders.split(","):
        os.makedirs(f"{output_folder}/{case}/{folder}", exist_ok=True)
    return output_folder, case

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