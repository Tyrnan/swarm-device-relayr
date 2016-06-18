#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""
Test publishing device data via MQTT to relayr cloud.

This subscribes to a given MQTT topic and publishes messages
for this topic, so it receives the same messages previously
posted.

This code needs the paho-mqtt package to be installed, e.g.
with "pip install paho-mqtt>=1.1".
"""

__author__ = 'ala'

import json
import time
import sys

#import paho.mqtt.client as mqtt
import serial
from SwarmResultParser import SwarmResultParser
from DistanceData import DistanceData
import script

def main():
    try:
        serport = sys.argv[1]
        print(serport)
        my_id = int(sys.argv[2], 16)
        print(my_id)
    except:
        print('Usage ' + sys.argv[0] + "<serial device>")

    try:
        ser = serial.Serial(
            port=serport,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0)
    except serial.SerialException, se:
        print("Serial Connection error" + se.message)
        return

    #try:
    print("BEGIN")
    script.load_zones()
    parser = SwarmResultParser()
    measurements = dict()
    while True:
        #client.loop()

        line = ser.readline()
        result = parser.parse_result(line.splitlines(True))

        for res in result:
            #print(res.type())
            if res.type() == "RRN":
                # publish data
                if not res.data:
                    continue
                vals = res.data()[0].strip("\r\n").split(",")
                if len(vals) < 4:
                    continue
                if int(vals[2]) != 0:
                    continue
                if int(vals[0], 16) != my_id:
                    continue
                dest = int(vals[1], 16)
                if not dest in measurements:
                    measurements[dest] = DistanceData(dest, 20)

                measurements[dest].add_observation(int(vals[3]))
                res = {'node_id': dest, 'distance': measurements[dest].get_filtered_value()}
                print(json.dumps(res))
                #script.handle_data(res)
                time.sleep(1)
    #except Exception, e:
    #    print("Exception occurred" + e.message)
    #    exit(-1)


if __name__ == '__main__':
    main()

