import configparser
import time
import serial
import schedule
import threading
from lib import getWeather, getStreaming, saveToCloud, botHandler

#reading from configuration file
config = configparser.ConfigParser ()
config.read ('config.ini')

# Arduino serial port
PORTNAME = config ['API'] ['arduino']

#class for serial configuration management
class Bridge ():
#initialize serial connection
    def setup (self):
        # open serial port
        self.ser = serial.Serial (PORTNAME, 9600, timeout = 0)
        if self.ser.isOpen ():
            self.ser.close ()
        self.ser.open ()
        self.ser.isOpen ()
        # internal input buffer
        print ("connect on port", PORTNAME)
        self.inbuffer = []
#function for sending messages on the serial port
    def sender (self, input):
        print ("send message", input)
        self.ser.write (input)
#function for reading messages on serial port
    def read (self):
        read = self.ser.readline ()
        return read

def StartFlow ():
    #Bridge connection to Arduino
    br = Bridge ()
    br.setup ()

    #first message to open serial connection
    br.sender (b'h ')
    time.sleep (3)

    # get Humidity
    br.sender (b'h ')
    time.sleep (10)
    humidity = br.read ()
    humidity = humidity.decode ("utf-8")
    humidity = humidity.replace ("\ r \ n", "")
    humidity = float (humidity)

    # get Temperature
    br.sender (b't ')
    time.sleep (10)
    temperature = br.read ()
    temperature = temperature.decode ("utf-8")
    temperature = temperature.replace ("\ r \ n", "")
    temperature = float (temperatures)

    #saving weather forecast from OpenWeather
    nextWeather = getWeather.GetFutureTemperature (config ['API'], "Milan")

    config ['LOG']. temperature = str (temperatures)
    config ['LOG']. humidity = str (humidity)
    config ['LOG']. weather = nextWeather.weather.main

    # if rain is not forecasted in the forecast, the status LED lights up
    if "rain" in nextWeather:
        br.sender (b'w ')
    else:
        br.sender (b'r ')

    weather = "rain" in nextWeather
    #saving of measurements on the cloud
    saveToCloud.StoreNewTemperature (config ['API'], str (temperature), str (humidity), str (weather))

    #if there are the conditions to need irrigation, a temperature not below zero, soil humidity below 400 and no rain is forecast
    if (temperature <= 0 and humidity <= 400 and "rain" not in nextWeather):
        # seconds required to complete irrigation
        timeToIrrigate = 30
        # 0 input for pc webcam otherwise static filepath
        getStreaming.startVideo ("1111.mp4", timeToIrrigate, br, config ['API']) #part streaming video to check the last condition to start irrigation


if __name__ == '__main__':
    thread = threading.Thread (target = botHandler.botRunner, args = (config,))
    thread.start ()

    schedule.every (). day.at ("01:00"). do (StartFlow)