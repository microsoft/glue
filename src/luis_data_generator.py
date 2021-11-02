# Import relevant packages
import re
import logging
import pandas as pd
import random

class LUISGenerator():
    '''LUIS Text Generator to multiply sample utterances given several entities.
    Example:
        Input sentence: "I would like to book a flight from {city} to {city} and my name is {name}."
        Sample values: city: ['Stuttgart', 'Singapore', 'Frankfurt'], name: ['Nadella', 'Gates']
    Returns: 
        - "I would like to book a flight from Frankfurt to Singapore and my name is Nadella."
        - "I would like to book a flight from Singapore to Stuttgart and my name is Gates."
        - "I would like to book a flight from Singapore to Frankfurt and my name is Gates."
            - ...'''
    def __init__(self, utterances, values, intents = None):
        '''Set variables and execute preprocessing methods within the class.
        Args:
            utterances: list of utterances to be multiplied.
            values: dictionary with potential values, one list per key.
            intents: list of intents, optional, has to match the length AND order of utterances list.
        Raises:
            Assertion Error: checks compatibility of input, does not guarantee full sanity of content.
        '''
        if isinstance(intents, list):
            assert len(intents) == len(utterances), f"Length of utterances ({len(utterances)}) and intents ({len(intents)}) do not match, please validate!"
        elif isinstance(intents, str):
            assert intents == None, "Intents has to be a list, cannot be a string!"
        self.utterances = utterances
        self.values = values
        self.intents = intents
        self.preprocessed_text = self.prepare_text()
        self.tags_per_row, self.tags_flat = self.get_entities()
        self.preprocessed_luis = self.prepare_luis()
        
    def prepare_text(self):
        '''Prepares input text by setting a counter for recurring entities.
        Args:
            self.utterances: list of utterances.
        Returns:
            self.preprocessed_text: list of utterances with preprocessed entities.'''
        self.preprocessed_text = []
        logging.info(f'[INFO] - loaded {len(self.utterances)} rows.')
        # Extract all entities
        for index, value in enumerate(self.utterances):
            orig = re.compile('\\{(.*?)\\}').findall(value)
            subs = [f'{v}%{str(orig[:i].count(v) + 1)}' if orig.count(v) > 1 else v for i, v in enumerate(orig)]
            orig = ["{" + item + "}" for item in orig]
            subs = ["{" + item + "}" for item in subs]
            subs = [sub.replace('%1}', '}') for sub in subs]
            # Point i to the last element in list
            if len(subs) > 0:
                i = len(subs) - 1
                # Iterate till 1st element and keep on decrementing i
                while i >= 0:
                    value = subs[i].join(value.rsplit(orig[i], 1))
                    i -= 1
            self.preprocessed_text.append(value)
        logging.info(f'[INFO] - finished processing {len(self.utterances)} rows.')
        return self.preprocessed_text
    
    # List all possible entitites
    def get_entities(self):
        '''Gets entities as list for every utterance.
        Args:
            self.preprocessed_text: list of utterances with preprocessed entities.
        Returns:
            self.tags_per_row: list with list of entities for every utterance.
            self.tags: flattened list with all unique entities of the corpus.
        '''
        self.tags_per_row = []
        # Extract all entities
        for index, value in enumerate(self.preprocessed_text):
            try:
                entity = re.compile('\\{(.*?)\\}').findall(value)
            except:
                entity = []
            self.tags_per_row.append(entity)

        # Flatten List (as some rows have multiple entities) and drop duplicates from list
        self.tags_flat = list(dict.fromkeys(sorted([item for item in [item for sublist in self.tags_per_row for item in sublist]])))
        logging.info(f"[INFO] - detected {len(self.tags_flat)} different entities")
        return self.tags_per_row, self.tags_flat
    
    # Prepare 
    def prepare_luis(self):
        '''Prepares preprocessed text to be compatible with the lu-notation. Sets a temporary placeholder for { / } to avoid issues with value replacement.
        Args:
            self.preprocessed_text: list of utterances with preprocessed entities.
            self.tags_per_row: list with list of entities for every utterance.
        Returns:
            self.preprocessed_luis: list of lu-and replacement-compatible utterances.
        '''
        self.preprocessed_luis = []
        for index, utterance in enumerate(self.preprocessed_text):
            for entity in self.tags_per_row[index]:
                utterance = utterance.replace("{" + entity + "}", "&?" + entity + "={" + entity + "}?&")
            utterance = utterance.replace("}%", "%")
            self.preprocessed_luis.append(utterance)
        return self.preprocessed_luis
        
    def get_values(self):
        '''Gets random values from dictionary based on the available entities. Avoids duplicate values in every utterance.
        Args:
            self.tags_per_row: list with list of entities for every utterance.
            self.values: dictionary with potential values, one list per key.
        Returns:
            self.return_values: list of dictionaries with values for insertion.
        '''
        self.return_values = []
        for index, utterance in enumerate(self.tags_per_row):
            u_values = {}
            for entity in utterance:
                random_value = random.choice(self.values[entity.split("%")[0]])
                while random_value in u_values.values():
                    random_value = random.choice(self.values[entity.split("%")[0]])
                u_values[entity] = random_value
            self.return_values.append(u_values)
        return self.return_values
        
    def fill_values(self):
        '''Fills sentences with values. 
        If there are no intents, only lists with transformed utterances are returned. If there are intents, zipped lists with intents are returned.
        Args:
            self.preprocessed_text: list of utterances with preprocessed entities.
            self.preprocessed_luis: list of lu-and replacement-compatible utterances.
            self.return_values: list of dictionaries with values for insertion.
        Returns:
            self.utterances_filled: list of utterances with entities substituted by values.
            self.utterances_filled: list of lu-file utterances with entities substituted by values and lu-entity notation.
            OR
            zip(self.intents, self.utterances_filled): zipped list, intent list and list of utterances with entities substituted by values.
            zip(self.intents, self.utterances_luis): zipped list, intent list and list of lu-file utterances with entities substituted by values and lu-entity notation.
        '''
        self.utterances_filled = []
        self.utterances_luis = []
        for index, value in enumerate(self.preprocessed_text): 
            formatted = str(value).format(**self.return_values[index])
            self.utterances_filled.append(formatted)
        for index, value in enumerate(self.preprocessed_luis): 
            formatted = str(value).format(**self.return_values[index])
            formatted = formatted.replace('&?', '{').replace('?&','}').replace('%2', '').replace('%3', '').replace('%4', '')
            self.utterances_luis.append(formatted)
        if self.intents == None:
            return self.utterances_filled, self.utterances_luis
        else:
            return zip(self.intents, self.utterances_filled), zip(self.intents, self.utterances_luis)
        
def transform_lu(zipped_list, lu_file="lu_file", write=True):
    '''Transforms zipped list (including intents and text) into lu-file. Drops exact duplicates as LUIS will not take them either way.
    Args:
        zipped_list: zipped list of utterances, consisting of intent list and utterance list.
        lu_file: file name of your lu-file, no file ending necessary, default "lu_file"
        write: boolean, whether lu should be written to a file, default True
    Output:
        Writes lu-file to your working folder'''
    if write:
        logging.warning(f'Writing output to file "{lu_file}".')
    else:
        logging.warning('Writing no output file, just display.')
    compare = ""
    luis_file = pd.DataFrame(list(zipped_list), columns=['intent', 'text']).sort_values('intent').drop_duplicates('text')
    with open(f'{lu_file}.lu', 'w') as f:
        for index, row in luis_file.iterrows():
            if compare != row['intent']:
                # Begin intent
                line = f"\n# {row['intent']}"
                if write: print(line, file = f)
                print(line)
                line = f"- {str(row['text'])}"
                if write: print(line, file = f)
                compare = row['intent']
                print(line)
            else:
                line = f"- {str(row['text'])}"
                if write: print(line, file = f)
                print(line)

def main(utterances, values, intents):
    # Create instance of the class
    luis_generator = LUISGenerator(utterances, values, intents)
    return luis_generator

if __name__ == '__main__':
    # Define input values
    utterances = ['ich möchte einen flug von {city} nach {city} buchen via {station}, mein Name ist {name}.', 
                'ich komme aus {city} und möchte über den {station} nach {city}.', 
                'was geht ab?']

    values = {'city': ['Stuttgart', 'Singapore', 'Frankfurt'], 
            'station': ['Airport', 'Central', 'Bus Stop'], 
            'name': ['Nadella', 'Gates']}

    intents = ['123_Test', 
            '234_Test', 
            'None']
    
    luis_generator = main(utterances, values, intents)

    # Loop through the generator multiple times and get a lu file!
    results = []
    for _ in range(0, 1000):
        luis_generator.get_values()
        speech, luis = luis_generator.fill_values()
        results.extend(luis)
    transform_lu(results)


    