import json
import logging
import os

import azure.functions as func

# Load keys
luis_id = os.environ.get('LUIS_ID')
luis_key = os.environ.get('LUIS_KEY')
if luis_key is None:
    # Local debugging
    import sys
    sys.path.append('./')
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    luis_id = config['luis']['appid']
    luis_key = config['luis']['key']

try:
    from __app__ import helper as he
except Exception as e:
    logging.info('[INFO] Main: Using local imports.')
    import LicensePlate.helper as he

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('[INFO] LicensePlate Post Processing started.')

    # Get query
    try:
        query = req.params.get('query')
    except Exception as e:
        logging.info(f'[INFO] Local debugging -> {e}')
        query = req['query']
    
    if query:

        # Get LUIS entity results
        try:
            r = he.score_luis(query, luis_id, luis_key)
            r_ent = r.get('entities')[0]
        except IndexError:
            r_ent = None

        # Process LP 
        if r_ent and r_ent.get('type') == 'platenumber':

            ## Load entity
            start = r_ent["startIndex"]
            end = r_ent["endIndex"]
            entity = query[start:end+1].lower()

            ## Extract and format LP
            raw, lp, split, valid, ambig = he.get_lp(query, entity)

            ## Format response
            cpl_entities, cpl_query = he.format_output(query, lp, split, valid, start, end, ambig)
            res = json.dumps(dict(
                        id              =   1,
                        query           =   query,
                        cplQuery        =   cpl_query,
                        cplEntities     =   cpl_entities,
                        entities        =   [r_ent],
                        topScoringIntent=   r["topScoringIntent"]
                        )
                    )
        else:
            res = json.dumps(dict(
                        id              =   1,
                        query           =   query,
                        cplQuery        =   query,
                        cplEntities     =   [{"entity":"", "type":"", "entitysplit":{}}],
                        entities        =   r["entities"],
                        topScoringIntent=   r["topScoringIntent"]
                        )
                    )
        return func.HttpResponse(res, mimetype='application/json')
    else:
        return func.HttpResponse(
             "[ERROR] Received a blank request. Please pass a value using the defined format. Example: \{'query':'AB C 1234'\}",
             status_code=400
        )

        