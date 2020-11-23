################################
# Checking I2S Input in Python
################################
#
import pyaudio

audio = pyaudio.PyAudio() # start pyaudio
for ii in range(0,audio.get_device_count()):
    # print out device info
    dev = audio.get_device_info_by_index(ii) # device name
    print('Device Name: {}'.format(dev['name']))
    for param in list(dev.keys()):
        print('\t {0}: {1}'.format(param,dev[param])) # device parameter info
