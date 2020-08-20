''' PARAMETER COLLECTOR '''
import configparser
import sys

def get_params():
    # Get config file
    sys.path.append('./')
    config = configparser.ConfigParser()
    global output_folder, app_id, key, region_luis, luis_endpoint, slot, speech_key, endpoint, region_speech, synth_key, region_synth, resource_name, language, font
    try:
        config.read('config.ini')
        output_folder = config['dir']['output_folder']
        app_id = config['luis']['app_id']
        key = config['luis']['key']
        region_luis = config['luis']['region']
        luis_endpoint = config['luis']['endpoint']
        slot = config['luis']['slot']
        speech_key = config['speech']['key']
        endpoint = config['speech']['endpoint']
        region_speech = config['speech']['region']
        synth_key = config['synth']['key']
        region_synth = config['synth']['region']
        resource_name = config['synth']['resource_name']
        language = config['synth']['language']
        font = config['synth']['font']
    except Exception as e:
        sys.exit(f'[EXCEPT] - Config file could not be loaded -> {e}.')