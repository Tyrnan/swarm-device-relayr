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

import paho.mqtt.client as mqtt
import serial

from credentials import creds

# ATTENTION !!!
# DO NOT try to set values under 200 ms of the server
# will kick you out
publishing_period = 500


class ResultData(object):
    __slots__ = ['__timestamp', '__type', '__data', '__opcode']

    def __init__(self, ts, thetype, data, opcode=-1):
        self.__timestamp = ts
        self.__type = thetype
        self.__data = data
        self.__opcode = opcode

    def timestamp(self):
        return self.__timestamp

    def type(self):
        return self.__type

    def data(self):
        return self.__data

    def opcode(self):
        return self.__opcode


class MqttDelegate(object):
    "A delegate class providing callbacks for an MQTT client."

    def __init__(self, client, credentials):
        self.client = client
        self.credentials = credentials

    def on_connect(self, client, userdata, flags, rc):
        print('Connected.')
        # self.client.subscribe(self.credentials['topic'].encode('utf-8'))
        self.client.subscribe(self.credentials['topic'] + 'cmd')

    def on_message(self, client, userdata, msg):
        print('Command received: %s' % msg.payload)

    def on_publish(self, client, userdata, mid):
        print('Message published.')


class SwarmResultParser(object):
    def __init__(self):
        pass

    def parse_result(self, result):
        ret = []
        it = iter(result)
        #for (ts, line) in it:
        for (line) in it:
            data = []
            # handle multiline results
            if line.startswith('#'):
                length = int(line[1:4])
                for i in range(length):
                    data.append(next(it))
                ret.append(ResultData(0, "multiline", data))
                continue

            # handle single line result
            if line.startswith('='):
                data.append(line[1:])
                ret.append(ResultData(0, "simple", data))
                continue

            # handle notifications
            if line.startswith('*'):
                parts = line[1:].split(':')
                if len(parts) < 2:
                    continue
                data.append(parts[1])
                ret.append(ResultData(0, parts[0], data))
                continue

            # handle sniffer response
            if line.startswith('<'):
                data.append(line)
                ret.append(ResultData(0, "sniffer", data))

            data.append(line)
            ret.append(ResultData(0, "unknown", data))
        return ret


def main(credentials, publishing_period):
    client = mqtt.Client(client_id=credentials['clientId'])
    delegate = MqttDelegate(client, creds)
    client.on_connect = delegate.on_connect
    client.on_message = delegate.on_message
    client.on_publish = delegate.on_publish
    user, password = credentials['user'], credentials['password']
    client.username_pw_set(user, password)
    # client.tls_set(cafile)
    # client.tls_insecure_set(False)
    try:
        serport = sys.argv[1]
        print(serport)
    except:
        print ('Usage ' + sys.argv[0] + "<serial device>")

    try:
        print('Connecting to mqtt server.')
        server, port = credentials['server'], credentials['port']
        client.connect(server, port=port, keepalive=60)
    except:
        print('Connection failed, check your credentials!')
        return

    # set 200 ms as minimum publishing period
    if publishing_period < 200:
        publishing_period = 200

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

    try:
        parser = SwarmResultParser()
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
                    message = [
                        {
                            'meaning': 'source',
                            'value': int(vals[0], 16)
                        },
                        {
                            'meaning': 'dest',
                            'value': int(vals[1], 16)
                        },
                        {
                            'meaning': 'distance',
                            'value': int(vals[3])
                        },
                        {
                            'meaning': 'rssi',
                            'value': int(vals[5])
                        },
                        {
                            'meaning': 'blinkId',
                            'value': int(vals[6])
                        },
                        {
                            'meaning': 'timestamp',
                            'value': int(vals[7])
                        }
                    ]
                    print(json.dumps(message))
                    #client.publish(credentials['topic'] + 'data', json.dumps(message))

                    time.sleep(publishing_period / 1000.)
    except Exception, e:
        print("Exception occurred" + e.message)
        exit(-1)

if __name__ == '__main__':
    main(creds, publishing_period)

