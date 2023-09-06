from scipy.fft import rfft
from scipy.fftpack import rfftfreq
from scipy.signal import hilbert
from scipy.stats import kurtosis
import array
import pandas
import numpy
import matplotlib.pyplot
import sys

file_name = sys.argv[1]
Fs = int(sys.argv[2])
FFT_PT = int(sys.argv[3])
file_csv = pandas.read_csv(file_name, nrows=FFT_PT)

matrix2 = file_csv[file_csv.columns[0]].to_numpy()
time_domain_data = matrix2.tolist()

print("Data Samples ", len(time_domain_data))

time_domain_data = [i * 1000 for i in time_domain_data]

fig, plts = matplotlib.pyplot.subplots(2)

fig.suptitle("Signal Analysis")
freq_data = rfft(time_domain_data)
freq_data = numpy.absolute(freq_data)

freq_data = [i * 2 / len(time_domain_data) for i in freq_data]
freq_steps = rfftfreq(len(freq_data), d=1./Fs)

plts[0].plot(time_domain_data)
plts[0].set_ylabel("Acceleration (mg)")
plts[0].set_xlabel("Time (n)")

kur = int(kurtosis(freq_data))
plts[1].plot(freq_steps, freq_data)
plts[1].set_ylabel("Acceleration (mg)")
plts[1].set_xlabel("Frequency (Hz)")

matplotlib.pyplot.show()

