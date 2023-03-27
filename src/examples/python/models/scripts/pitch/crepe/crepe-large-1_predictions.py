from essentia.standard import MonoLoader, PitchCREPE

audio = MonoLoader(filename="audio.wav", sampleRate=16000)()
model = PitchCREPE(graphFilename="crepe-large-1.pb")
time, frequency, confidence, activations = model(audio)