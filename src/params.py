''' PARAMETER COLLECTOR '''
import configparser
import sys

def get_params(parser):
    '''
    Collect arguments from command line
    '''
    parser.add_argument("--input",
                    type=str,
                    default="input/example_testset_flights.txt",
                    help="give the whole path to tab-delimited file")
    parser.add_argument("--subfolder",
                    default="input",
                    type=str,
                    help="Input folders, pass comma-separated if multiple ones")
    parser.add_argument("--audio_files",
                    default="input/audio/",
                    type=str,
                    help="Input folders, pass comma-separated if multiple ones")
    parser.add_argument("--treshold",
                    default=0.85,
                    type=float,
                    help="Set minimum confidence score between 0.00 and 1.00")
    parser.add_argument("--do_transcribe",
                    default=False,
                    action="store_true",
                    help="Input folder of audio files")
    parser.add_argument("--do_scoring",
                    default=False,
                    action="store_true",
                    help="Text to speech using Microsoft Speech API")
    parser.add_argument("--do_synthesize",
                    default=False,
                    action="store_true",
                    help="Text to speech using Microsoft Speech API")
    parser.add_argument("--do_evaluate",
                    default=False,
                    action="store_true",
                    help="Evaluate speech transcriptions")
    parser.add_argument("--do_lufile",
                    default=False,
                    action="store_true",
                    help="Create LU-file")
    args = parser.parse_args()
    return args

def get_config():
    '''
    Collect parameters from config file
    '''
    # Get config file
    sys.path.append('./')
    config = configparser.ConfigParser()
    global output_folder, luis_appid, luis_key, luis_region, luis_endpoint, luis_slot, stt_key, stt_endpoint, stt_region, tts_key, tts_region, tts_resource_name, tts_language, tts_font
    try:
        config.read('config.ini')
        output_folder = config['dir']['output_folder']
        luis_appid = config['luis']['app_id']
        luis_key = config['luis']['key']
        luis_region = config['luis']['region']
        luis_endpoint = config['luis']['endpoint']
        luis_slot = config['luis']['slot']
        stt_key = config['speech']['key']
        stt_endpoint = config['speech']['endpoint']
        stt_region = config['speech']['region']
        tts_key = config['synth']['key']
        tts_region = config['synth']['region']
        tts_resource_name = config['synth']['resource_name']
        tts_language = config['synth']['language']
        tts_font = config['synth']['font']
    except Exception as e:
        sys.exit(f'[EXCEPT] - Config file could not be loaded -> {e}.')

def main():
    return None

if __name__ == '__main__':
    main()