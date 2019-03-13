'''
Assignment to learn how to interpolate data1
'''
import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
import pandas as pd
from datetime import datetime as dt

# https://youtu.be/-zvHQXnBO6c
def read_wx_data(wx_file, harbor_data):
    """
    Read temperature and time data from file.
    Populates the harbor_data dictionary with two lists: wx_times and wx_temperatures
    :param wx_file: File object with data
    :param harbor_data: A dictionary to collect data.
    :return: Nothing
    """
    wx_data = pd.read_csv(wx_file)  # a dataframe that holds the data from "TempPressure.txt"
    
    temp = list(wx_data["Time"])    # a list of strings
    # Convert string time to float hours for easier plotting
    init_time = temp[0]             # take first time which will be your time zero
    harbor_data["wx_times"] = []    # list to hold the data
    for h_time in temp:
        delta_t = dt.strptime(h_time, '%H:%M:%S') - dt.strptime(init_time, '%H:%M:%S')  # get delta time
        harbor_data["wx_times"].append(float(delta_t.total_seconds()/3600))             # convert to hours

    harbor_data["wx_temperatures"] = wx_data["Ch1:Deg F"]   # Places temperatures in harbor_data


def read_gps_data(gps_file, harbor_data):
    """
    Read gps and altitude data from file.
    Populates the harbor_data dictionary with two lists: gps_times and gps_altitude
    :param gps_file: File object with gps data
    :param harbor_data: A dictionary to collect data.
    :return: Nothing
    """
    header_names = ["GPS HOURS", "MIN", "SEC", "MET (MIN)", "LONG (decimal deg)", "LAT (decimal deg)", "ALT (ft)"]      
    gps_data = pd.read_csv(gps_file, sep='\t', skiprows=2, usecols=[0,1,2,6], names=header_names)
    times = {}
    times = gps_data["GPS HOURS"].apply(str) + ":" + gps_data["MIN"].apply(str) + ":" + gps_data["SEC"].apply(str)
    
    temp = list(times)    # a list of strings
    # Convert string time to float hours for easier plotting
    init_time = temp[0]             # take first time which will be your time zero
    harbor_data["gps_times"] = []    # list to hold the data
    for h_time in temp:
        delta_t = dt.strptime(h_time, '%H:%M:%S') - dt.strptime(init_time, '%H:%M:%S')  # get delta time
        harbor_data["gps_times"].append(float(delta_t.total_seconds()/3600))             # convert to hours

    harbor_data["gps_altitude"] = gps_data["ALT (ft)"]  # Places altitudes in harbor_data


def interpolate_wx_from_gps(harbor_data):
    """
    Compute wx altitudes by interpolating from gps altitudes
    Populates the harbor_data dictionary with four lists:
        1) wx correlated altitude up
        2) wx correlated temperature up
        3) wx correlated altitude down
        4) wx correlated temperature down
    :param harbor_data: A dictionary to collect data.
    :return: Nothing
    """
    # print(harbor_data["gps_altitude"])
    # print(harbor_data["gps_times"])

    # Lists to hold the interpolated data
    harbor_data["wx_temp_up"] = []
    harbor_data["wx_alt_up"] = []
    harbor_data["wx_temp_down"] = []
    harbor_data["wx_alt_down"] = []
    
    altitude_peak = 0       # Holds peak altitude of balloon
    altitude_peak_time = 0  # Holds time balloon peaks

    # Finds peak altitude and peak altitude time
    for count, altitude in enumerate(harbor_data["gps_altitude"]):
        if altitude > altitude_peak:
            altitude_peak = altitude
        else:
            altitude_peak_time = harbor_data["gps_times"][count]
            break

    # Populates lists of temperatures up and temperatures down
    for count, time in enumerate(harbor_data["wx_times"]):
        if time < altitude_peak_time:
            harbor_data["wx_temp_up"].append(harbor_data["wx_temperatures"][count])
        elif time > harbor_data["gps_times"][len(harbor_data["gps_times"])-1]:
            break
        else:
            harbor_data["wx_temp_down"].append(harbor_data["wx_temperatures"][count])

    # Populates lists of altitudes up and altitudes down
    harbor_data["wx_alt_up"] = np.linspace(harbor_data["gps_altitude"][0], altitude_peak, len(harbor_data["wx_temp_up"]))
    harbor_data["wx_alt_down"] = np.linspace(altitude_peak, harbor_data["gps_altitude"][len(harbor_data["gps_altitude"])-1], len(harbor_data["wx_temp_down"]))


def plot_figs(harbor_data):
    """
    Plot 2 figures with 2 subplots each.
    :param harbor_data: A dictionary to collect data.
    :return: nothing
    """
    # Creates two subplots to show the temperature/time and altitude/time separately
    # Temperature over time data
    plt.subplot(2, 1, 1)
    plt.plot(harbor_data["wx_times"], harbor_data["wx_temperatures"])
    plt.xlim([0,2.35])
    plt.title("Harbor Flight Data")
    plt.ylabel("Temperature, F")
    # Altitude over time data
    plt.subplot(2, 1, 2)
    plt.plot(harbor_data["gps_times"], harbor_data["gps_altitude"])
    plt.xlabel("Mission Elapsed Time, Hours")
    plt.ylabel("Altitude, Feet")
    plt.show()

    # Creates two subplots to show the AltUp/TempUp and AltDown/TempDown separately
    # Altitude up over temperature up data
    plt.subplot(1,2,1)
    plt.plot(harbor_data["wx_temp_up"], harbor_data["wx_alt_up"])
    plt.title("Harbor Ascent Flight Data")
    plt.xlabel("Temperature, F")
    plt.ylabel("Altitude, Feet")
    # Altitude down over temperature down data
    plt.subplot(1,2,2)
    plt.plot(harbor_data["wx_temp_down"], harbor_data["wx_alt_down"])
    plt.title("Habor Descent Flight Data")
    plt.xlabel("Temperature, F")
    plt.show()


def main():
    """
    Main function
    :return: Nothing
    """
    harbor_data = {}
    wx_file = sys.argv[1]                   # first program input param
    gps_file = sys.argv[2]                  # second program input param

    read_wx_data(wx_file, harbor_data)      # collect weather data
    read_gps_data(gps_file, harbor_data)    # collect gps data
    interpolate_wx_from_gps(harbor_data)    # calculate interpolated data
    plot_figs(harbor_data)                  # display figures


if __name__ == '__main__':
    main()
    exit(0)
