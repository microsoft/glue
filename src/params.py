''' PARAMETER COLLECTOR '''
import configparser
import sys

def get_params(parser):
    """Collect arguments from command line
    Args:
        parser: ArgumentParser-object
    Returns:
        args: Object with parsed arguments
    """
    parser.add_argument("--input",
                    type=str,
                    #default="assets/input_files/example_tts.csv", # Uncomment for debugging
                    help="Path to comma-separated text input file")
    parser.add_argument("--subfolder",
                    default="input",
                    type=str,
                    help="Input folders, pass comma-separated if multiple ones")
    parser.add_argument("--audio",
                    type=str,
                    help="Path to folder with audio files")
    parser.add_argument("--do_transcribe",
                    default=False,
                    action="store_true",
                    help="Activate speech-to-text processing")
    parser.add_argument("--do_scoring",
                    default=False,
                    action="store_true",
                    help="Activate LUIS model scoring")
    parser.add_argument("--do_synthesize",
                    default=False,
                    action="store_true",
                    help="Activate text-to-speech synthetization")
    parser.add_argument("--do_evaluate",
                    default=False,
                    action="store_true",
                    help="Activate evaluation of transcriptions based on reference transcriptions")
    args = parser.parse_args()
    return args

def get_config(fname_config='config.ini'):
    """Collect parameters from config file
    Args:
        fname_config: file name of config file
    Returns:
        Sets parsed arguments as global variables
    """
    # Get config file
    sys.path.append('./')
    config = configparser.ConfigParser()
    global output_folder, driver, luis_appid, luis_key, luis_region, luis_endpoint, luis_slot, luis_treshold, stt_key, stt_endpoint, stt_region, tts_key, tts_region, tts_resource_name, tts_language, tts_font
    try:
        config.read(fname_config)
        output_folder = config['dir']['output_folder']
        stt_key = config['stt']['key']
        stt_endpoint = config['stt']['endpoint']
        stt_region = config['stt']['region']
        tts_key = config['tts']['key']
        tts_region = config['tts']['region']
        tts_resource_name = config['tts']['resource_name']
        tts_language = config['tts']['language']
        tts_font = config['tts']['font']
        luis_appid = config['luis']['app_id']
        luis_key = config['luis']['key']
        luis_region = config['luis']['region']
        luis_endpoint = config['luis']['endpoint']
        luis_slot = config['luis']['slot']
        luis_treshold = float(config['luis']['treshold'])
        luis_treshold = 0 if luis_treshold == '' else luis_treshold
        driver = config['driver']['path']
    except Exception as e:
        sys.exit(f'[EXCEPT] - Config file could not be loaded -> {e}.')

def main():
    return None

if __name__ == '__main__':
    main()