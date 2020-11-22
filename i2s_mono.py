##############################################
# INMP441 MEMS Microphone + I2S Module
##############################################
#
# -- Frequency analysis with FFTs and saving
# -- .wav files of MEMS mic recording
#
# --------------------------------------------
# -- by Josh Hrisko, Maker Portal LLC
# --------------------------------------------
# 
##############################################
#
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import time,wave,datetime,os,csv

##############################################
# function for FFT
##############################################
#
def fft_calc(data_vec):
    data_vec = data_vec*np.hanning(len(data_vec)) # hanning window
    N_fft = len(data_vec) # length of fft
    freq_vec = (float(samp_rate)*np.arange(0,int(N_fft/2)))/N_fft # fft frequency vector
    fft_data_raw = np.abs(np.fft.fft(data_vec)) # calculate FFT
    fft_data = fft_data_raw[0:int(N_fft/2)]/float(N_fft) # FFT amplitude scaling
    fft_data[1:] = 2.0*fft_data[1:] # single-sided FFT amplitude doubling
    return freq_vec,fft_data
#
##############################################
# function for setting up pyserial
##############################################
#
def pyserial_start():
    audio = pyaudio.PyAudio() # create pyaudio instantiation
    ##############################
    ### create pyaudio stream  ###
    # -- streaming can be broken down as follows:
    # -- -- format             = bit depth of audio recording (16-bit is standard)
    # -- -- rate               = Sample Rate (44.1kHz, 48kHz, 96kHz)
    # -- -- channels           = channels to read (1-2, typically)
    # -- -- input_device_index = index of sound device
    # -- -- input              = True (let pyaudio know you want input)
    # -- -- frmaes_per_buffer  = chunk to grab and keep in buffer before reading
    ##############################
    stream = audio.open(format = pyaudio_format,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=CHUNK)
    stream.stop_stream() # stop stream to prevent overload
    return stream,audio

def pyserial_end():
    stream.close() # close the stream
    audio.terminate() # close the pyaudio connection
#
##############################################
# function for plotting data
##############################################
#
def plotter(plt_1=0,plt_2=0):
    plt.style.use('ggplot')
    plt.rcParams.update({'font.size':16})
    ##########################################
    # ---- time series and full-period FFT
    if plt_1:
        fig,axs = plt.subplots(2,1,figsize=(12,8)) # create figure
        ax = axs[0] # top axis: time series
        ax.plot(t_vec,data,label='Time Series') # time data
        ax.set_xlabel('Time [s]') # x-axis in time
        ax.set_ylabel('Amplitude') # y-axis amplitude
        ax.legend(loc='upper left')

        ax2 = axs[1] # bottom axis: frequency domain
        ax2.plot(freq_vec,fft_data,label='Frequency Spectrum')
        ax2.set_xscale('log') # log-scale for better visualization
        ax2.set_yscale('log') # log-scale for better visualization
        ax2.set_xlabel('Frequency [Hz]')# frequency label
        ax2.set_ylabel('Amplitude') # amplitude label
        ax2.legend(loc='upper left')

        # peak finder labeling on the FFT plot
        max_indx = np.argmax(fft_data) # FFT peak index
        ax2.annotate(r'$f_{max}$'+' = {0:2.1f}Hz'.format(freq_vec[max_indx]),
                     xy=(freq_vec[max_indx],fft_data[max_indx]),
                     xytext=(2.0*freq_vec[max_indx],
                             (fft_data[max_indx]+np.mean(fft_data))/2.0),
                     arrowprops=dict(facecolor='black',shrink=0.1)) # peak label
        
    ##########################################
    # ---- spectrogram (FFT vs time)
    if plt_2:
        fig2,ax3 = plt.subplots(figsize=(12,8)) # second figure
        t_spec = np.reshape(np.repeat(t_spectrogram,np.shape(freq_array)[1]),np.shape(freq_array))
        y_plot = fft_array # data array
        spect = ax3.pcolormesh(t_spec,freq_array,y_plot,shading='nearest') # frequency vs. time/amplitude
        ax3.set_ylim([20.0,20000.0]) 
        ax3.set_yscale('log') # logarithmic scale in freq.
        cbar = fig2.colorbar(spect) # add colorbar
        cbar.ax.set_ylabel('Amplitude',fontsize=16) # amplitude label

    fig.subplots_adjust(hspace=0.3)
    fig.savefig('I2S_time_series_fft_plot.png',dpi=300,
                bbox_inches='tight')
    plt.show() # show plot
#
##############################################
# function for grabbing data from buffer
##############################################
#
def data_grabber(rec_len):
    stream.start_stream() # start data stream
    stream.read(CHUNK,exception_on_overflow=False) # flush port first 
    t_0 = datetime.datetime.now() # get datetime of recording start
    print('Recording Started.')
    data,data_frames = [],[] # variables
    for frame in range(0,int((samp_rate*rec_len)/CHUNK)):
        # grab data frames from buffer
        stream_data = stream.read(CHUNK,exception_on_overflow=False)
        data_frames.append(stream_data) # append data
        data.append(np.frombuffer(stream_data,dtype=buffer_format))
    stream.stop_stream() # stop data stream
    print('Recording Stopped.')
    return data,data_frames,t_0
#
##############################################
# function for analyzing data
##############################################
#
def data_analyzer(chunks_ii):
    freq_array,fft_array = [],[]
    t_spectrogram = []
    data_array = []
    t_ii = 0.0
    for frame in chunks_ii:
        freq_ii,fft_ii = fft_calc(frame) # calculate fft for chunk
        freq_array.append(freq_ii) # append chunk freq data to larger array
        fft_array.append(fft_ii) # append chunk fft data to larger array
        t_vec_ii = np.arange(0,len(frame))/float(samp_rate) # time vector
        t_ii+=t_vec_ii[-1] 
        t_spectrogram.append(t_ii) # time step for time v freq. plot
        data_array.extend(frame) # full data array
    t_vec = np.arange(0,len(data_array))/samp_rate # time vector for time series
    freq_vec,fft_vec = fft_calc(data_array) # fft of entire time series
    return t_vec,data_array,freq_vec,fft_vec,freq_array,fft_array,t_spectrogram
#
##############################################
# Save data as .wav file and .csv file
##############################################
#
def data_saver(t_0):
    data_folder = './data/' # folder where data will be saved locally
    if os.path.isdir(data_folder)==False:
        os.mkdir(data_folder) # create folder if it doesn't exist
    filename = datetime.datetime.strftime(t_0,
                                          '%Y_%m_%d_%H_%M_%S_pyaudio') # filename based on recording time
    wf = wave.open(data_folder+filename+'.wav','wb') # open .wav file for saving
    wf.setnchannels(chans) # set channels in .wav file 
    wf.setsampwidth(audio.get_sample_size(pyaudio_format)) # set bit depth in .wav file
    wf.setframerate(samp_rate) # set sample rate in .wav file
    wf.writeframes(b''.join(data_frames)) # write frames in .wav file
    wf.close() # close .wav file
    return filename
#
##############################################
# Main Data Acquisition Procedure
##############################################
#   
if __name__=="__main__":
    #
    ###########################
    # acquisition parameters
    ###########################
    #
    CHUNK          = 44100  # frames to keep in buffer between reads
    samp_rate      = 44100 # sample rate [Hz]
    pyaudio_format = pyaudio.paInt16 # 16-bit device
    buffer_format  = np.int16 # 16-bit for buffer
    chans          = 1 # only read 1 channel
    dev_index      = 0 # index of sound device    
    #
    #############################
    # stream info and data saver
    #############################
    #
    stream,audio = pyserial_start() # start the pyaudio stream   
    record_length =  5 # seconds to record
    input('Press Enter to Record Noise (Keep Quiet!)')
    noise_chunks,_,_ = data_grabber(CHUNK/samp_rate) # grab the data
    input('Press Enter to Record Data (Turn Freq. Generator On)')
    data_chunks,data_frames,t_0 = data_grabber(record_length) # grab the data
    data_saver(t_0) # save the data as a .wav file
    pyserial_end() # close the stream/pyaudio connection
    #
    ###########################
    # analysis section
    ###########################
    #
    _,_,_,fft_noise,_,_,_ = data_analyzer(noise_chunks) # analyze recording
    t_vec,data,freq_vec,fft_data,\
            freq_array,fft_array,t_spectrogram = data_analyzer(data_chunks) # analyze recording
    # below, we're subtracting noise
    fft_array = np.subtract(fft_array,fft_noise)
    freq_vec = freq_array[0]
    fft_data = np.mean(fft_array[1:,:],0)
    fft_data = fft_data+np.abs(np.min(fft_data))+1.0
    plotter(plt_1=1,plt_2=0) # select which data to plot
    #  ^(plt_1 is time/freq), ^(plt_2 is spectrogram) 
