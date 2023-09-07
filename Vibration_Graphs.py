# Syntax 
# $ python Vibration_Graphs <csv file path> <Sampling Frequency> <FFT Points>

# Example
# $ python Vibration_Graphs ./x.csv 12800 1024

from scipy.fft import rfft
from scipy.fftpack import rfftfreq
import array
import pandas
import numpy
import matplotlib.pyplot
import sys

file_name = sys.argv[1] #Argument 1 is the .csv (Column 0 includes acceleration in g)
Fs = int(sys.argv[2]) #Argument 2 is the Sampling Frequency in Hz
FFT_PT = int(sys.argv[3]) #Argument 3 is the number of FFT points (the file should have enough samples)
file_csv = pandas.read_csv(file_name, nrows=FFT_PT)

matrix = file_csv[file_csv.columns[0]].to_numpy()
time_domain_data = matrix.tolist()

#Convert to mg
time_domain_data = [i * 1000 for i in time_domain_data] 

fig, (timeDomainPlt, FreqDomainPlt) = matplotlib.pyplot.subplots(2)

fig.suptitle("Signal Analysis")

#Run Real FFT
freq_data = rfft(time_domain_data)

#Extract Magnitude 
freq_data = numpy.absolute(freq_data)

#Descale to get magnitude in mg
freq_data = [i * 2.0 / FFT_PT for i in freq_data]
freq_steps = rfftfreq(len(freq_data), d=1./Fs)

timeDomainPlt.plot(time_domain_data)
timeDomainPlt.set_ylabel("Acceleration (mg)")
timeDomainPlt.set_xlabel("Time (n)")

FreqDomainPlt.plot(freq_steps, freq_data)
FreqDomainPlt.set_ylabel("Acceleration (mg)")
FreqDomainPlt.set_xlabel("Frequency (Hz)")

matplotlib.pyplot.show()

