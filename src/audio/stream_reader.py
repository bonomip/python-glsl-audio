####
####
#### https://github.com/aiXander/Realtime_PyAudio_FFT/blob/master/src/stream_reader_pyaudio.py
####
####

import pyaudio
import wave
import time
from utils import numpy_data_buffer, np
from collections import deque

CHUNK = 1024
FORMAT= pyaudio.paInt16
CHANNELS= 1
RATE = 44100
UPDATES_PER_SECONDS  = 1000

VERBOSE = False

### StreamReader CLASS
class StreamReader:
    #init class (todo: make it modular by passing costant as argument)
    #init so you can have two shaders having different input
    #but maybe it's only a plus and will never be usefull
    def __init__(self):
        self.pa = pyaudio.PyAudio()

        #propagating constants
        self.rate = RATE
        self.chunk = CHUNK
        self.format = FORMAT
        self.channels = CHANNELS
        self.updates_per_seconds = UPDATES_PER_SECONDS
        #used by stream analyzer
        self.new_data = False
        #debug
        self.verbose = False
        if self.verbose:
            self.data_capture_delays = deque(maxlen=20)
            self.num_data_captures = 0

        #self.print_available_devices()
        
        #setting the input device
        self.device = 4 #quickitime player input
        self.info = self.pa.get_device_info_by_index(self.device)
        #open audio stream
        self.stream = self.pa.open(
                        #input_device_index=self.device,
                        format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk,
                        stream_callback=self.non_blocking_stream_read)

        self.print_setup()
    #start stream
    def stream_start(self, data_windows_to_buffer = None):
        #self.data_windows_to_buffer = data_windows_to_buffer

        if data_windows_to_buffer is None:
            self.data_windows_to_buffer = int(self.updates_per_second / 2) #By default, buffer 0.5 second of audio
        else:
            self.data_windows_to_buffer = data_windows_to_buffer

        self.data_buffer = numpy_data_buffer(self.data_windows_to_buffer, self.chunk)

        print("\n-- Starting live audio stream...\n")
        self.stream.start_stream()
        self.stream_start_time = time.time()
    #terminate stream
    def terminate(self):
        print("Sending stream termination command...")
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
    #to be understood
    def non_blocking_stream_read(self, in_data, frame_count, time_info, status):
        if self.verbose:
            start = time.time()

        if self.data_buffer is not None:
            self.data_buffer.append_data(np.frombuffer(in_data, dtype=np.int16))
            self.new_data = True

        if self.verbose:
            self.num_data_captures += 1
            self.data_capture_delays.append(time.time() - start)

        return in_data, pyaudio.paContinue
    ###### UTILITIES FUNCTIONS
    def print_setup(self):
        print("\n##################################################################################################")
        print("\nDefaulted to using first working mic, Running on:")
        self.print_mic_info(self.device)
        print("\n##################################################################################################")
        print('Recording from %s at %d Hz\nUsing (non-overlapping) data-windows of %d samples (updating at %.2ffps)'
            %(self.info["name"],self.rate, self.chunk, self.updates_per_seconds))
        
    def print_available_devices(self):
        for i in range(self.pa.get_device_count()):
            print(self.pa.get_device_info_by_index(i))

    def print_mic_info(self, mic):
        mic_info = self.pa.get_device_info_by_index(mic)
        print('\nMIC %s:' %(str(mic)))
        for k, v in sorted(mic_info.items()):
            print("%s: %s" %(k, v))

    def record_and_save(self):
        frames = []
        seconds = 5

        for i in range(0, int(self.rate/self.chunck * seconds)):
            data = self.stream.read(self.chunck)
            frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

        print("record stopped")   

        wf = wave.open("o.wav", 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pa.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
### END StreamReader CLASS