import os
import time
import numpy
import soundfile
from datetime import datetime
from PIL import Image
import pandas
import pynmea2 as nmea
import matplotlib.pyplot as plt

ftpDirectoryPath = 'C:/Users/dwigh/Desktop/FTP/'
ftpFiles = os.listdir(ftpDirectoryPath)

def formatFiles(directory, rawFile):
    with open(directory + rawFile) as rawFP:
        moduleDataLine = rawFP.readline()
        formattedDataFile = open('formatted/' + rawFile, 'w')
        while moduleDataLine:
            formatedData = moduleDataLine.replace('&', '\n&\n')
            formattedDataFile.write(formatedData)
            moduleDataLine = rawFP.readline()
    rawFP.close()

def parseFiles(readDirectory, writeDirectory):
    readDirectoryFiles = os.listdir(readDirectory)
    for readFile in readDirectoryFiles:
        currentFile = open(readDirectory + readFile, 'r').readlines()
        audioFile = open(writeDirectory + 'audio/' + readFile, 'w')
        audioFile.write(currentFile[2].replace(' ', '\n').strip())
        audioFile.close()
        seismicFile = open(writeDirectory + 'seismic/' + readFile, 'w')
        seismicFile.write(currentFile[4].replace('_', '\n').strip())
        seismicFile.close()
        imageFile = open(writeDirectory + 'image/' + readFile, 'w')
        imageFile.write(currentFile[6].replace('_', '\n').strip())
        imageFile.close()
        gpsFile = open(writeDirectory + 'gps/' + readFile, 'w')
        for i in range(8, 14):
            gpsFile.write(currentFile[i].replace('_',''))
        gpsFile.close()

def processAudio(rawDirectory, duration, targetDirectory):
    rawFiles = os.listdir(rawDirectory)
    for file in rawFiles:
        print(file)
        rawData = open(rawDirectory + file, 'r').readlines()
        length = len(rawData)
        sampleRate = length/duration
        buffer = [0 for i in range(length)]
        scaled = [0 for i in range(length)]
        for i in range(0,length):
            scaled[i] = float(int(rawData[i]) * 2)/1023
        scaled = numpy.asarray(scaled)
        file.replace('.txt','')
        soundfile.write(targetDirectory + '/' + file.replace('.txt', '.wav'), scaled, int(sampleRate))

def processImage(rawDirectory, targetDirectory):
    rawFiles = os.listdir(rawDirectory)
    for file in rawFiles:
        rawData = open(rawDirectory + file, 'r').readlines()
        buffer = [0 for i in range(len(rawData))]
        for i in range(1,len(rawData)-1):
            buffer[i] = int(rawData[i])
        byteData = bytes(buffer)
        imgSize = (320,320)
        img = Image.frombytes('L', imgSize, byteData)
        img.save(targetDirectory + file.replace('txt', 'jpg'))

def processSeismic(rawDirectory, targetDirectory):
    rawFiles = os.listdir(rawDirectory)
    for file in rawFiles:
        rawData = pandas.read_csv(rawDirectory + file, delimiter=' ')
        rawData.to_csv(targetDirectory + 'csv/' + file.replace('.txt', '.csv'), index=None)
        counter = 0
        for col in rawData.columns:
            counter += 1
            plt.figure()
            plt.plot(rawData[col])
            column = 'x' if counter == 1 else 'y' if counter == 2 else 'z'
            plt.savefig(targetDirectory + 'plot/' + column + '-' + file.replace('.txt', '.png'))

def processGPS(rawDirectory, targetDirectory):
    rawFiles = os.listdir(rawDirectory)
    for file in rawFiles:
        rawData = open(rawDirectory + file, 'r').readline()
        msg = nmea.parse(rawData)
        # print(msg)
        gpsFile = open(targetDirectory + file, 'w')
        gpsFile.write(f'{msg.latitude}\n')
        gpsFile.write(f'{msg.longitude}\n')
        gpsFile.write(f'{msg.timestamp}')
        gpsFile.close()

def main():
    oldFTPFiles = ftpFiles
    while(1):
        newFTPFiles = os.listdir(ftpDirectoryPath)
        # processImage('parsed/image/', 'processed/image/')
        if(oldFTPFiles != newFTPFiles):
            print('ARGUS II --> FTP Updated ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S %p"))
            time.sleep(5)
            for rawFile in newFTPFiles:
                formatFiles(ftpDirectoryPath, rawFile)
            print('ARGUS II --> DATA REFORMATTED ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S %p"))
            parseFiles('formatted/', 'parsed/')
            # time.sleep(15)
            print('ARGUS II --> DATA PARSED ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S %p"))
            processAudio('parsed/audio/', 50, 'processed/audio/')
            print('ARGUS II --> AUDIO PROCESSING COMPLETE ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S %p"))
            processImage('parsed/image/', 'processed/image/')
            print('ARGUS II --> IMAGE PROCESSING COMPLETE ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S %p"))
            processSeismic('parsed/seismic/', 'processed/seismic/')
            print('ARGUS II --> SEISMIC PROCESSING COMPLETE ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S %p"))
            processGPS('parsed/gps/', 'processed/gps/')
            print('ARGUS II --> GPS PROCESSING COMPLETE ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S %p"))
        oldFTPFiles = newFTPFiles

if __name__ == "__main__":
    main()