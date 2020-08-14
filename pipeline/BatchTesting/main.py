import logging
import json
import azure.functions as func

# Custom Function
try:
    import evaluate as ev
except:
    from __app__.BatchTesting import evaluate as ev

def prepare_ref(text):
    """Remove tags from reference data"""
    try:
        return text.replace('<variation>','').replace('<variable>','').replace('<unknown>','')
    except Exception as e:
        print(f'[ERROR] Could not process reference text -> {e}')
        return text

def to_percentage(score):
    try:
        return round(score, 3) * 100
    except:
        return score

def main(req: func.HttpRequest) -> func.HttpResponse:
    '''Function returns evaluation results for transcribed text.

    - Input
    Lists of reference and transcribed texts

    - Output
    WER metric
    '''
    logging.info('Python HTTP trigger function processed a request.')

    try:
        data = json.loads(req.get_body())
    except:
        data = req

    if data:
        ids = []
        ref = []
        rec = []
        lp_ids = []
        lp_ref = []
        lp_rec = []

        for line in data:
            try:
                l_ref = prepare_ref(line['ref'])
                l_rec = line['rec']
                l_ids = line['id']
                ref.append(l_ref)
                rec.append(l_rec)
                ids.append(l_ids)
                if 'lp_ref' in line:
                    lp_ids.append(line['id'])
                    lp_ref.append(line['lp_ref'])
                    lp_rec.append(line['lp_rec'])
            except Exception as e:
                logging.info(f'[WARNING] The following line could not be processed: {line}')
        
        # STT Error List
        stt = ev.EvaluateTranscription()
        wer, wrr, ser, l_ref, l_rec, l_cor = stt.calculate_metrics(ref, rec, print_verbosiy=2)
        l_results = []
        for i, rf, rc, c in zip(ids, l_ref, l_rec, l_cor):
            l_results.append(dict(
                    id = i,
                    ref = rf,
                    rec = rc, 
                    score = to_percentage(c)      
                )
            )
        ## Additional error details
        l_ins, l_del, l_sub = stt.print_errors(min_count=1)
        l_details = dict(
            insertions = l_ins,
            deletions = l_del,
            substitutions = l_sub
        )

        # LPR Error List
        lp_results = []
        lp_ser = 0
        lp_total = 0
        if len(lp_ref) > 0:
            __, __, __lp_ser, lp_ref, lp_rec, lp_cor = ev.EvaluateTranscription(case_lower=False, lpr=True).calculate_metrics(lp_ref, lp_rec, print_verbosiy=2)
            for i, rf, rc, c in zip(lp_ids, lp_ref, lp_rec, lp_cor):
                lp_results.append(dict(
                        id = i,
                        ref = rf,
                        rec = rc, 
                        score = to_percentage(c)
                    )
                )
                lp_total += c
            lp_ser = lp_total / len(lp_cor)

        res = json.dumps(dict(
            metrics = dict(
                count = len(data),
                wer = to_percentage(wer),
                wrr = to_percentage(wrr),
                ser = to_percentage(ser),
                lpr = to_percentage(lp_ser)
            ), 
            stt = l_results,
            stt_details = l_details,
            lpr = lp_results
        ))
        return func.HttpResponse(res, mimetype='application/json')
    else:
        return func.HttpResponse(
             f"Please pass a list of objects in the request body.",
             status_code=400
        )