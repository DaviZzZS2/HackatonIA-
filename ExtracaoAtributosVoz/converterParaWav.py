from pydub import AudioSegment

# OPUS -> WAV
audio = AudioSegment.from_file("teste.waptt.opus", format="opus")
audio = audio.set_frame_rate(44100).set_channels(1).set_sample_width(2)
audio.export("teste.wav", format="wav")
