from TTS.api import TTS
from TTS.utils.manage import ModelManager
import simpleaudio as sa
import torch

# since PyTorch 2-6 wee need to allow pickle import explicit and load the german model
from TTS.utils.radam import RAdam
with torch.serialization.safe_globals({RAdam}):
    tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False, gpu=False)


# wave file output path
output_path = "output.wav"

# list all available models
manager = ModelManager()
models = manager.list_models()
for m in models:
    print(m)

# convert text to speech
tts.tts_to_file(text="Guten Morgen! Ich bin dein Sprachassistent. "
                     "Ich kann dir Fragen zu den Fischen stellen, und dir das Ergebniss des Agenten ansagen!", file_path=output_path)

# play the wavefile
wave_obj = sa.WaveObject.from_wave_file(output_path)
wave_obj.play().wait_done()