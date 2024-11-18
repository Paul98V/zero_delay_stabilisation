# -*- coding: utf-8 -*-


import os
# Change the working directory
os.chdir(r'C:\Users\lab_user\Desktop\piezo_control')
#%%
from scipy.fft import fft
import numpy as np
import _avs_py as avs
import matplotlib.pyplot as plt
#from matplotlib.animation import FuncAnimation
import keyboard
from scipy.signal import savgol_filter
# from scipy.signal import find_peaks
import time
# from piezo_run import move
from statistics import mean
from math import pi
from matplotlib import gridspec
# from piezo_run import move
from simple_pid import PID

handle = 1
x_data = avs.AVS_GetLambda(handle)
S_pixel =    50      #This is the window for s golay filter
S_poly =    7        #This is the polynomial order for sgolay filter

# Set integration time
integration_time = int(input('Enter integration time in ms and press Enter: '))
print(f'Setting integration time to {integration_time} ms...')
measconfig = avs.MeasConfig_DefaultValues(handle)
measconfig.m_IntegrationTime = integration_time


print('Block laser to take background and press enter')
keyboard.wait("enter")
[timestamp, bkgd_spectrum] = avs.acquire_single_spectrum(1)
bkgd_spectrum_smooth = savgol_filter(bkgd_spectrum,S_pixel, S_poly)
print('Block laser path 1 to take background and press enter')
keyboard.wait("enter")
print("Background from the first source captured. Press Shift to continue after 2 seconds...")
[timestamp, bkgd_spectrum1] = avs.acquire_single_spectrum(1)
bkgd_spectrum1_smooth = savgol_filter(bkgd_spectrum1,S_pixel, S_poly)

print('Block laser path 2 to take background and press enter')
keyboard.wait("enter")
print("Background from the second source captured. Press Shift to continue after 2 seconds...")
[timestamp, bkgd_spectrum2] = avs.acquire_single_spectrum(1)
bkgd_spectrum2_smooth = savgol_filter(bkgd_spectrum2,S_pixel, S_poly)


Data2 = bkgd_spectrum2_smooth - bkgd_spectrum_smooth
Data1 = bkgd_spectrum1_smooth - bkgd_spectrum_smooth

Data2[161:len(Data2)] = 0
Data1[161:len(Data1)] = 0

weighted_avg_wavelength2 = np.sum(x_data*Data2) / np.sum(Data2)
print(weighted_avg_wavelength2)

weighted_avg_wavelength1 = np.sum(x_data*Data1) / np.sum(Data1)
print(weighted_avg_wavelength1)

lamda = mean([weighted_avg_wavelength2, weighted_avg_wavelength1])
print(lamda)


#%%
import serial
# import time
# \from math import pi

def move(i):
    """Move the piezo one time to value i and take a measurement"""
    # Return measurement

    COM = 'COM11'
    baudrate = 115200
    timeout = 0.25

    NV200 = serial.Serial(COM, baudrate, timeout=timeout, xonxoff=True)

    NV200.write(b'\r')
    print(NV200.readline().decode(), end='')

    NV200.write(b'modsrc,0\r')
    NV200.write(b'cl,1\r')

    command = f'set,{i:.3f}\r'  # Format the floating-point value with 3 decimal places
    NV200.write(command.encode())
    NV200.write(b'meas\r')
    measurement = NV200.readline().decode()
    print(float(command[4:len(command)]))
    print(float(measurement[5:len(measurement)]))
    
    while abs(float(command[4:len(command)]) - float(measurement[5:len(measurement)])) >= 0.01:
        print(1)
        NV200.write(command.encode())
        NV200.write(b'meas\r')
        measurement = NV200.readline().decode()
    print(f'Measurement at {i:.3f} micrometers: {measurement}', end='')
    return float(measurement[5:13]) 

if __name__ == "__main__":
    pass


# def PiezoCurrent(i):
#     """Move the piezo one time to value i and take a measurement"""
#     # Return measurement

#     COM = 'COM4'
#     baudrate = 115200
#     timeout = 0.25

#     NV200 = serial.Serial(COM, baudrate, timeout=timeout, xonxoff=True)

#     #NV200.write(b'\r')
#     #print(NV200.readline().decode(), end='')

#     #NV200.write(b'modsrc,0\r')
#     #NV200.write(b'cl,1\r')

#     #command = f'set,{i:.2f}\r'  # Format the floating-point value with 2 decimal places
#     #NV200.write(command.encode())
#     #time.sleep(1)
#     NV200.write(b'meas\r')
#     measurement = NV200.readline().decode()
#     #print(f'Measurement at {i:.2f} micrometers: {measurement}', end='')
#     print(float(measurement[5:13]))
#     return float(measurement[5:13]) 

# if __name__ == "__main__":
#     pass


piezo_orig = 100.000  #original position of piezo
move(float(piezo_orig))

#%%
plt.figure(101)
plt.plot(x_data, bkgd_spectrum_smooth)
plt.plot(x_data, bkgd_spectrum2_smooth)
plt.plot(x_data, bkgd_spectrum1_smooth)
plt.xlim(1000 ,1400)


#%%
#%matplotlib qt
#plt.ion()
plt.figure(100)
plt.plot(x_data, Data1)
plt.plot(x_data, Data2)

#%%
[timestamp, spectrum] = avs.acquire_single_spectrum(1)
spectrum_smooth = savgol_filter(spectrum, S_pixel, S_poly)
spectrum_smooth = spectrum_smooth - bkgd_spectrum_smooth


spectrum_fft = fft(spectrum_smooth)

spectrum_fft_try = spectrum_fft[12:40]

peak =  np.argmax(np.abs(spectrum_fft_try))

print(peak)

plt.figure(10)
plt.plot(np.abs(spectrum_fft_try))

plt.figure(12)
plt.plot(x_data, spectrum_smooth)

#%%
import csv
import os
# Change the working directory
os.chdir(r'C:\Users\lab_user\Desktop\piezo_control')


# # Define file names with timestamps to avoid overwriting
timestamp = time.strftime("%Y%m%d%H%M%S")
# spectrum_file = f'spectrum_data_{timestamp}.csv'
# fft_file = f'fft_data_{timestamp}.csv'
phase_file = f'phase_data_{timestamp}.csv'

# # Check if the files already exist and create headers if not
# # if not os.path.exists(spectrum_file):
# #     with open(spectrum_file, 'w', newline='') as csvfile:
# #         writer = csv.writer(csvfile)
# #         writer.writerow(["Timestamp", "Spectrum"])
# # if not os.path.exists(fft_file):
# #     with open(fft_file, 'w', newline='') as csvfile:
# #         writer = csv.writer(csvfile)
# #         writer.writerow(["fft_xaxis", "FFT"])
if not os.path.exists(phase_file):
    with open(phase_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["No. of shots", "Phase"])
        
plt.ion()  # Turn on interactive mode
fig = plt.figure(figsize=(8, 6))
gs = gridspec.GridSpec(3, 1, height_ratios=[1,0.5, 2])

# fig = plt.figure(figsize=(16, 6))
# ax1 = fig.add_subplot(131)
# ax2 = fig.add_subplot(132)
# ax3 = fig.add_subplot(133)

ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])
ax3 = plt.subplot(gs[2])

# Initialize empty lists to store data for each plot
times = []
phases = []
phasehold = []
average_phase = 0  # Initialize average_phase
zeros =   []

# Create the initial plots
line1, = ax1.plot([], [])
line4, = ax1.plot([], [])
line2, = ax2.plot([], [])
line3, = ax3.plot([], [])
line5, = ax3.plot([], [])

# Add labels and titles for the plots
ax1.set_xlabel("Wavelength")
ax1.set_ylabel("Spectral Intensity")
ax1.set_title("Spectrum")

ax2.set_xlabel("Frequency")
ax2.set_ylabel("Amplitude")
ax2.set_title("Fourier")

# ax3.set_xlabel("Time")
ax3.set_xlabel("No. of shots")
ax3.set_ylabel("Phase")
ax3.set_title("Phase vs. Time")
peak_positions = []
plt.show()

# Initialize the starting value of p
p = 0
step_size = 1
num_points = 10000
intial_sample_size = 20
pid = PID(0.5, 0.1, 0.06, setpoint=0)
piezo_current = piezo_orig

try:
    while p <= num_points:
        p += 1
        [timestamp, spectrum] = avs.acquire_single_spectrum(1)
        spectrum_smooth = savgol_filter(spectrum, S_pixel, S_poly)
        spectrum_smooth = spectrum_smooth - bkgd_spectrum_smooth

       
        zeros.append(0)
        if p == 1:
            time_zero = timestamp
            
        if p == 25:
            overlay_spec = spectrum_smooth
        #print(np.round(timestamp - time_zero, 2))

        spectrum_fft = fft(spectrum_smooth)
        abs_spectrum_fft = np.abs(spectrum_fft)

        fft_xaxis = np.linspace(0, len(spectrum_fft), len(spectrum_fft))
        

        spectrum_fft_try = spectrum_fft[12:40]
        peak =  np.argmax(np.abs(spectrum_fft_try))
        #peak_index = peak + 12  # Adjust for the slice [12:40]
        peak_positions.append(peak)
        peakhold = int(np.mean(peak_positions))
        print(peakhold)
        # phase_difference = (phase - average_phase)
        ######## PID LOGIC #######
        
        if p<= intial_sample_size:
            phase = np.angle(spectrum_fft_try[peak])
            phasehold.append(phase)
            peak_mean = np.mean(peak_positions)
            peak_mean = int(np.round(peak_mean,0))
            overlay_spec = spectrum_smooth
            initial_phase =np.mean(phasehold)
        else:
            phase = np.angle(spectrum_fft_try[peak_mean])
            output = pid(phase)
            piezomove = lamda*output/(4*pi*1e3)
            print(np.round(piezomove,3))
            print(p)
            phase_difference = phase - initial_phase
            if phase_difference<2.5:
                # move(piezo_current - np.round(piezomove,3))
                # piezo_current = PiezoCurrent(1)
                piezo_current = move(piezo_current - np.round(piezomove,3))
         
            
        phases.append(phase)
        times.append(np.round(timestamp - time_zero, 2))
        
        
        if np.remainder(p,10) == 0:
            line1.set_data(x_data, spectrum_smooth)
            line2.set_data(fft_xaxis, abs_spectrum_fft)
        
            line4.set_data(x_data, overlay_spec)
        
        # line3.set_data(times, phases)
            
            line3.set_data(range(1, p+1), phases)
            line5.set_data(range(1, p+1), zeros)

        # Update the plots with the new data
            ax1.relim()
            ax1.set_xlim(1000, 1600)
            ax1.autoscale_view()
    
            ax2.relim()
            ax2.autoscale_view()
    
            # Clear the previous peak markers and plot the new ones
            ax2.clear()
            ax2.plot(fft_xaxis, abs_spectrum_fft)
            ax2.set_xlim(10, 75)
            ax2.set_ylim(0, 10000)
            ax2.scatter(peak_positions, [abs_spectrum_fft[j] for j in peak_positions], c='red', marker='o', label='Peaks')
            ax2.legend()
    
            ax3.relim()
            ax3.set_ylim(-3.5, 3.5)
            ax3.autoscale_view()
        
        # # Save the data to CSV files
        # with open(spectrum_file, 'a', newline='') as csvfile:
        #     writer = csv.writer(csvfile)
        #     writer.writerow([timestamp, spectrum_smooth])

        # with open(fft_file, 'a', newline='') as csvfile:
        #     writer = csv.writer(csvfile)
        #     writer.writerow([fft_xaxis, abs_spectrum_fft])

            with open(phase_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([times, phase])
            
            
            fig.canvas.flush_events()
            
           
            plt.pause(0.01)
except KeyboardInterrupt:
    pass

# Close the plots
# ...

finally:
    plt.ioff()
    plt.show()