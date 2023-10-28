from stream_analyzer import StreamAnalyzer
from stream_reader import StreamReader
import time

ear = StreamAnalyzer(StreamReader())

fps = 60  #How often to update the FFT features + display
last_update = time.time()

while True:
    if (time.time() - last_update) > (1./fps):
        last_update = time.time()
        raw_fftx, raw_fft, binned_fftx, binned_fft = ear.get_audio_features()

        ear.strongest_frequency #in Hz
        feature_values = ear.frequency_bin_energies[::-1] #this shoud be used as input

        for i in range(len(ear.frequency_bin_energies)):
            feature_value = feature_values[i] # each entry
            #i shhoud get the average between a arbitrary interval
            # low, mid, hi, freq