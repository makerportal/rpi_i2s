# I<sup>2</sup>S Microphone Recording on Raspberry Pi with Python
Python codes that read, save, and analyze audio input from I<sup>2</sup>S MEMS microphones on a Raspberry Pi

Raspberry Pi boards are capable of recording stereo audio using an interface called the inter-IC sound (I2S or I2S) bus. The I2S standard uses three wires to record data, keep track of timing (clock), and determine whether an input/output is in the left channel or right channel. First, the Raspberry Pi (RPi) needs to be prepped for I2S communication by creating/enabling an audio port in the RPi OS system. This audio port will then be used to communicate with MEMS microphones and consequently record stereo audio (one left channel, one right channel). Python iS then used to record the 2-channel audio via the pyaudio Python audio library. Finally, the audio data will be visualized and analyzed in Python with simple digital signal processing methods that include Fast Fourier Transforms (FFTs), noise subtraction, and frequency spectrum peak detection.

The full tutorial can be found at: https://makersportal.com/blog/recording-stereo-audio-on-a-raspberry-pi

## Mono Wiring 
![Mono I2S INMP441 Wiring](https://static1.squarespace.com/static/59b037304c0dbfb092fbe894/t/5fb82519c776377ef22d2462/1605904753804/i2s_rpi_INMP441.png?format=750w)

## Stereo Wiring
![Stereo I2S INMP441 Wiring](https://static1.squarespace.com/static/59b037304c0dbfb092fbe894/t/5fb8281d1e0ac17c5996ac51/1605904761696/i2s_rpi_INMP441_stereo.png?format=750w)

## Mono Output

*Example Output for 557Hz Test Frequency*:

![I2S Mono Test](./image_repo/I2S_time_series_fft_plot_white.png)

## Stereo Output

*Example Stereo Output for 1012Hz Test Frequency*:

![I2S Stereo Test](./image_repo/I2S_stereo_time_series_fft_plot_white.png)
