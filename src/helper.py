''' HELPER FUNCTIONS ACROSS MULTIPLE SCRIPTS '''
''' nonstoptimm@gmail.com '''

# Import standard packages
from datetime import datetime
import os
import uuid
import pandas as pd

# Helper Functions
def create_case(output_folder):
    """ Create case for project
    Args:
        output_folder: directory of output folder
    Returns:
        output_folder: directory of output folder
        case: name of the created case
        output_file: name of text output file
    """
    # Create Case
    case = f"{datetime.today().strftime('%Y%m%d')}-{uuid.uuid4().hex}"
    os.makedirs(f"{output_folder}/{case}", exist_ok=True)
    return output_folder, case

def create_df(fname):
    """Create df from LU-file"""
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
    return df

def write_lu(luis_file):
    """Write LU-file in the structure needed for Microsoft LUIS"""
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

def transform_notebook():
    #TODO
    return None