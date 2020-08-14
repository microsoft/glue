from __future__ import division

from functools import reduce
from collections import defaultdict
from edit_distance import SequenceMatcher
import string


class EvaluateTranscription():
    """Calculate various metrics for the speech transcription service.
    Required input:
    - Reference transcript (ground truth)
    - Recognized text

    Parameters:
    - case_lower (boolean)  : Lower case strings before evaluation
    - lpr (boolean)         : Accuracy of LPR
    
    Output:
    - WER : Word Error Rate
    - WRR : Word Recognition Rate 
    (number of matched words in recognized / number of words in the reference)
    - SER : Sentence Error Rate
    (number of incorrect sentences / total number of sentences)

    Implementation based on : https://github.com/belambert/asr-evaluation
    """

    def __init__(self, case_lower=True, lpr=False):
        self.case_lower = case_lower
        self.error_codes = ['replace', 'delete', 'insert']
        self.ref_list = []
        self.rec_list = []
        self.correct_list = []
        self.insertion_list = []
        self.deletion_list = []
        self.substitution_list = []

        if lpr:
            self.table = str.maketrans({key: None for key in string.punctuation if key is not '-'})
        else:
            self.table = str.maketrans({key: None for key in string.punctuation})

    def track_confusions(self, sm, seq1, seq2):
        """Keep track of the errors in a global variable, given a sequence matcher."""
        opcodes = sm.get_opcodes()
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'insert':
                for i in range(j1, j2):
                    word = seq2[i]
                    self.insertion_table[word] += 1
            elif tag == 'delete':
                for i in range(i1, i2):
                    word = seq1[i]
                    self.deletion_table[word] += 1
            elif tag == 'replace':
                for w1 in seq1[i1:i2]:
                    for w2 in seq2[j1:j2]:
                        key = (w1, w2)
                        self.substitution_table[key] += 1

    def get_match_count(self, sm):
        "Return the number of matches, given a sequence matcher object."
        matches = None
        matches1 = sm.matches()
        matching_blocks = sm.get_matching_blocks()
        matches2 = reduce(lambda x, y: x + y, [x[2] for x in matching_blocks], 0)
        assert matches1 == matches2
        matches = matches1
        return matches

    def get_error_count(self, sm):
        """Return the number of errors (insertion, deletion, and substitutiions
        , given a sequence matcher object."""
        opcodes = sm.get_opcodes()
        errors = [x for x in opcodes if x[0] in self.error_codes]
        error_lengths = [max(x[2] - x[1], x[4] - x[3]) for x in errors]
        return reduce(lambda x, y: x + y, error_lengths, 0)

    def print_diff(self, sm, seq1, seq2, prefix1='REF:', prefix2='REC:', suffix1=None, suffix2=None):
        """Given a sequence matcher and the two sequences, print a Sphinx-style
        'diff' off the two."""
        ref_tokens = []
        rec_tokens = []
        opcodes = sm.get_opcodes()
        for tag, i1, i2, j1, j2 in opcodes:
            # If they are equal, do nothing except lowercase them
            if tag == 'equal':
                for i in range(i1, i2):
                    ref_tokens.append(seq1[i].lower())
                for i in range(j1, j2):
                    rec_tokens.append(seq2[i].lower())
            # For insertions and deletions, put a filler of '***' on the other one, and
            # make the other all caps
            elif tag == 'delete':
                for i in range(i1, i2):
                    ref_token = seq1[i].upper()
                    ref_tokens.append(ref_token)
                for i in range(i1, i2):
                    rec_token = '*' * len(seq1[i])
                    rec_tokens.append(rec_token)
            elif tag == 'insert':
                for i in range(j1, j2):
                    ref_token = '*' * len(seq2[i])
                    ref_tokens.append(ref_token)
                for i in range(j1, j2):
                    rec_token = seq2[i].upper()
                    rec_tokens.append(rec_token)
            # More complicated logic for a substitution
            elif tag == 'replace':
                seq1_len = i2 - i1
                seq2_len = j2 - j1
                # Get a list of tokens for each
                s1 = list(map(str.upper, seq1[i1:i2]))
                s2 = list(map(str.upper, seq2[j1:j2]))
                # Pad the two lists with False values to get them to the same length
                if seq1_len > seq2_len:
                    for i in range(0, seq1_len - seq2_len):
                        s2.append(False)
                if seq1_len < seq2_len:
                    for i in range(0, seq2_len - seq1_len):
                        s1.append(False)
                assert len(s1) == len(s2)
                # Pair up words with their substitutions, or fillers
                for i in range(0, len(s1)):
                    w1 = s1[i]
                    w2 = s2[i]
                    # If we have two words, make them the same length
                    if w1 and w2:
                        if len(w1) > len(w2):
                            s2[i] = w2 + ' ' * (len(w1) - len(w2))
                        elif len(w1) < len(w2):
                            s1[i] = w1 + ' ' * (len(w2) - len(w1))
                    # Otherwise, create an empty filler word of the right width
                    if not w1:
                        s1[i] = '*' * len(w2)
                    if not w2:
                        s2[i] = '*' * len(w1)
                ref_tokens += s1
                rec_tokens += s2
        if suffix1: ref_tokens.append(suffix1)
        if suffix2: rec_tokens.append(suffix2)
        self.ref_list.append(' '.join(ref_tokens))
        self.rec_list.append(' '.join(rec_tokens))

    def print_errors(self, min_count=0):
        """Print the confused words that we found... grouped by insertions, deletions
        and substitutions.

        Parameters:
        - min_count         : Minimume occurance count for words in print error words.
        """
        pass
        if len(self.insertion_table) > 0:
            for item in sorted(list(self.insertion_table.items()), key=lambda x: x[1], reverse=True):
                if item[1] >= min_count:
                    self.insertion_list.append(dict(
                        string = item[0],
                        count = item[1]
                    ))
        if len(self.deletion_table) > 0:
            for item in sorted(list(self.deletion_table.items()), key=lambda x: x[1], reverse=True):
                if item[1] >= min_count:
                    self.deletion_list.append(dict(
                        string = item[0],
                        count = item[1]
                    ))
        if len(self.substitution_table) > 0:
            for [w1, w2], count in sorted(list(self.substitution_table.items()), key=lambda x: x[1], reverse=True):
                if count >= min_count:
                    self.substitution_list.append(dict(
                        string1 = w1,
                        string2 = w2,
                        count = count
                    ))
        return self.insertion_list, self.deletion_list, self.substitution_list

    def print_all(self, ref, rec, sm, id_=None):
        """Print a single instance of a ref/rec pair."""
        self.print_diff(sm, ref, rec)
        self.counter + 1

        # Handle cases where the reference is empty without dying
        if len(ref) != 0:
            correct_rate = sm.matches() / len(ref)
            error_rate = sm.distance() / len(ref)
        elif sm.matches() == 0:
            correct_rate = 1.0
            error_rate = 0.0
        else:
            correct_rate = 0.0
            error_rate = sm.matches()
        temp = 'Correct          = {0:6.1%}  {1:3d}   ({2:6d})'.format(correct_rate, sm.matches(), len(ref))
        temp = 'Errors           = {0:6.1%}  {1:3d}   ({2:6d})'.format(error_rate, sm.distance(), len(ref))
        self.correct_list.append(correct_rate)

    def calculate_metrics(self, ref, rec,
                ignore_punct=True,
                label=None,
                print_verbosiy=0, #0=Nothing, 1=errors, 2=all
                exclude=None,
                query_keyword=None):

            """Function to calculate the different metrics
            Parameters:
            - ignore_punct (bool)   : Ignore punctuation in evaluation (NOTE: no impact) 
            - print_verbosiy (int)  : 
                        0 = Print only metrics
                        1 = Print only errors
                        2 = Print allm errors and none errors
            - exclude (list)        : List of IDs to exclude
            - query_keyword (str)   : filter list using a string
            """
            self.counter = 0
            self.insertion_table = defaultdict(int)
            self.deletion_table = defaultdict(int)
            self.substitution_table = defaultdict(int)
            
            error_count = 0
            match_count = 0
            ref_token_count = 0
            sent_error_count = 0
            lengths = []
            error_rates = []
            wer_bins = defaultdict(list)
            wrr = 0.0
            wer = 0.0
            ser = 0.0
            id_ = ''

            for i, (ref_line, rec_line) in enumerate(zip(ref, rec)):
                if ignore_punct:
                    _ref = ref_line.translate(self.table).split()
                    _rec = rec_line.translate(self.table).split()
                else:
                    _ref = ref_line.split()
                    _rec = rec_line.split()

                if label is not None:
                    id_ = label[i]
                
                if exclude is not None:
                    if exclude in id_:
                        continue
                
                if self.case_lower:
                    _ref = list(map(str.lower, _ref))
                    _rec = list(map(str.lower, _rec))

                if query_keyword is not None:
                    if len([i for i in query_keyword if i in _ref]) == 0:
                        continue

                sm = SequenceMatcher(a=_ref, b=_rec)
                errors = self.get_error_count(sm)
                matches = self.get_match_count(sm)
                ref_length = len(_ref)

                # Increment the total counts we're tracking
                error_count += errors
                match_count += matches
                ref_token_count += ref_length
                self.counter += 1

                if errors != 0:
                    sent_error_count += 1

                self.track_confusions(sm, _ref, _rec)

                # If we're printing instances, do it here (in roughly the align.c format)
                if print_verbosiy == 2 or (print_verbosiy == 1 and errors != 0):
                    self.print_all(_ref, _rec, sm, id_=id_)

                lengths.append(ref_length)
                if len(_ref) > 0:
                    error_rate = errors * 1.0 / len(_ref)
                else:
                    error_rate = float("inf")
                error_rates.append(error_rate)
                wer_bins[len(_ref)].append(error_rate)

            # Compute WER and WRR
            if ref_token_count > 0:
                wrr = match_count / ref_token_count
                wer = error_count / ref_token_count

            # Compute SER
            if self.counter > 0:
                ser = sent_error_count / self.counter

            return wer, wrr, ser, self.ref_list, self.rec_list, self.correct_list