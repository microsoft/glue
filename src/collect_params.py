''' PARAMETER COLLECTOR '''
import configparser
import sys

def get_params(parser):
    '''
    Collect arguments from command line
    '''
    parser.add_argument("--input",
                    type=str,
                    default="input/testset-example.txt",
                    help="give the whole path to tab-delimited file")
    parser.add_argument("--mode",
                    default="score",
                    type=str,
                    help="Mode, either score or eval")
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

def main():
    return None

if __name__ == '__main__':
    main()