.venv\Scripts\activate

write-host "Scenario 1: Speech-to-Text (STT)"
write-host "################################"
write-host ""
python src/glue.py --audio assets\examples\input_files\audio --do_transcribe

write-host ""
write-host "Scenario 2: Text-to-Speech (TTS)"
write-host "################################"
write-host ""
python src/glue.py --input assets\examples\input_files\example_tts.csv --do_synthesize

write-host ""
write-host "Scenario 3: LUIS-Scoring"
write-host "################################"
write-host ""
python src/glue.py --input assets\examples\input_files\example_luis.csv --do_scoring

write-host ""
write-host "Scenario 4: Evaluation (STT)"
write-host "################################"
write-host ""
python src/glue.py --input assets\examples\output_files\example_transcriptions_full.csv --do_evaluate

write-host ""
write-host "Scenario 5: Speech to Text and Evaluation (STT)"
write-host "################################"
write-host ""
python src/glue.py --audio assets\examples\input_files\audio --input assets\examples\input_files\example_stt_eval.csv --do_transcribe --do_evaluate

write-host ""
write-host "Scenario 6: Speech to Text, Evaluation and LUIS-Scoring"
write-host "################################"
write-host ""
python src/glue.py --audio assets\examples\input_files\audio --input assets\examples\input_files\example_stt_eval_luis.csv --do_transcribe --do_evaluate --do_scoring

write-host ""
write-host "Scenario 7: Speech to Text and LUIS-Scoring"
write-host "################################"
write-host ""
python src/glue.py --audio assets\examples\input_files\audio --input assets\examples\input_files\example_luis.csv --do_transcribe --do_scoring