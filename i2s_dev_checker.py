################################
# Checking I2S Input in Python
################################
#
import pyaudio

audio = pyaudio.PyAudio() # start pyaudio
for ii in range(0,audio.get_device_count()):
    # print out device info
    print(audio.get_device_info_by_index(ii)) 
