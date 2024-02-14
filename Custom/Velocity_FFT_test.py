# Syntax 
# $ python Velocity_FFT.py <csv file path> <Sampling Frequency> <FFT Points>
# 
# Example
# $ python Velocity_FFT.py ./x.csv 12800 1024 

from scipy.fft import rfft
from scipy.fftpack import rfftfreq
import array
import pandas
import numpy
import matplotlib.pyplot
import sys
import math 
from scipy import integrate


file_name = sys.argv[1] #Argument 1 is the .csv (Column 0 includes acceleration in g)
Fs = int(sys.argv[2]) #Argument 2 is the Sampling Frequency in Hz
FFT_PT = int(sys.argv[3]) #Argument 3 is the number of FFT points (the file should have enough samples)

file_csv = pandas.read_csv(file_name, nrows=FFT_PT)

matrix = file_csv[file_csv.columns[0]].to_numpy()
time_domain_data = matrix.tolist()

###### Velocity FFT Using integration property of FFT recommended by NCD
#Convert to mg
time_domain_data = [i * 1000 for i in time_domain_data] 
#Run Real FFT
freq_data = rfft(time_domain_data)

#Extract Magnitude 
freq_data = numpy.absolute(freq_data)

#kill DC term 
freq_data[0] = 0
#Descale to get magnitude in mg
freq_data = [i * 2.0 / FFT_PT for i in freq_data]
freq_steps = rfftfreq(len(freq_data), d=1./Fs)
velocity_freq_data = [float(i * 9.81) for i in freq_data]
for i in range(1, len(freq_data)):
    wk = (2.0 * math.pi * (Fs / FFT_PT) * float(i))
    velocity_freq_data[i] = velocity_freq_data[i] / wk

matplotlib.pyplot.figure()
matplotlib.pyplot.title('Velocity FFT (Derived from Acceleration FFT)')
matplotlib.pyplot.plot(freq_steps, velocity_freq_data)
matplotlib.pyplot.ylabel("Velocity (mm/s)")
matplotlib.pyplot.xlabel("Frequency (Hz)")
###################################################################################

########################## fix for old ATS FFT #####################
###### Velocity FFT Using integration in Time-Domain then FFT
acc_time_in_mm_s2 = [i * 9.81 for i in time_domain_data] 
velocity_time_trapz = integrate.cumtrapz(y=acc_time_in_mm_s2, dx=1/Fs, initial=0)
velocity_freq_trapz = rfft(velocity_time_trapz)
#Extract Magnitude 
velocity_freq_trapz = numpy.absolute(velocity_freq_trapz)
velocity_freq_trapz[0] = 0
#Descale to get magnitude in mg
velocity_freq_trapz = [i * 2.0 / FFT_PT for i in velocity_freq_trapz]
matplotlib.pyplot.figure()
matplotlib.pyplot.title('Velocity FFT (Derived from Trapezoid Integration in time-domain)')
matplotlib.pyplot.plot(freq_steps, velocity_freq_trapz)
matplotlib.pyplot.ylabel("Velocity (mm/s)")
matplotlib.pyplot.xlabel("Frequency (Hz)")

#########################################################################ATS was doing like this####
###### Velocity FFT Using integration in Time-Domain then FFT (Faulty)
axis_samples = numpy.linspace(0.0, 1, num=len(acc_time_in_mm_s2))
velocity_time_trapz = integrate.cumtrapz(y=acc_time_in_mm_s2, x=axis_samples, initial=0)
velocity_freq_trapz = rfft(velocity_time_trapz)
#Extract Magnitude 
velocity_freq_trapz = numpy.absolute(velocity_freq_trapz)
velocity_freq_trapz[0] = 0
#Descale to get magnitude in mg
velocity_freq_trapz = [i * 2.0 / FFT_PT for i in velocity_freq_trapz]
matplotlib.pyplot.figure()
matplotlib.pyplot.title('Velocity FFT (Derived from Trapezoid Integration (FAULTY))')
matplotlib.pyplot.plot(freq_steps, velocity_freq_trapz)
matplotlib.pyplot.ylabel("Velocity (mm/s)")
matplotlib.pyplot.xlabel("Frequency (Hz)")

matplotlib.pyplot.show()
