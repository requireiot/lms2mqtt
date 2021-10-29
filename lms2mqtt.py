#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#   Copyright (C) 2019,2021 Bernd Waldmann
#
#   This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. 
#   If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/
#
#   SPDX-License-Identifier: MPL-2.0
#

#
# Daemon to read Squeezebox notifications and publish via MQTT
#

import os,sys,time,glob,signal,requests,errno
import logging,logging.handlers
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import telnetlib,urllib

#-------------------------------------------------------------
# logging

LMS_LOGNAME = 'lms2mqtt'
logger = logging.getLogger(LMS_LOGNAME)
formatter = logging.Formatter('%(levelname)-8s: '+LMS_LOGNAME+': %(message)s' )
logger.setLevel(logging.DEBUG)

handlerSyslog = logging.handlers.SysLogHandler(address = '/dev/log')
handlerSyslog.setFormatter(formatter)
handlerSyslog.setLevel(logging.INFO)
logger.addHandler(handlerSyslog)

handlerConsole = logging.StreamHandler(sys.stdout)
handlerConsole.setFormatter(formatter)
handlerConsole.setLevel(logging.DEBUG)
logger.addHandler(handlerConsole)

#-------------------------------------------------------------
# Constants pre-defined here, then read from /etc/default/bw
#

LMS_HOST = "media-server"

#----- MQTT constants
MQTT_BROKER = "ha-server"
MQTT_PUB_BASE_LMS = "lms/"

#----- try to read from /etc/default
DEFAULT_BW="/etc/default/bw"
if os.path.isfile(DEFAULT_BW):
    try:
        exec(open(DEFAULT_BW,'r').read())
        logger.info(
            "Read config from %s, publish as '%s'" %
            (DEFAULT_BW, MQTT_PUB_BASE_LMS))
    except:
        logger.warn( "Error reading %s" % DEFAULT_BW )

#-------------------------------------------------------------
# global variables
#
stopped = False
mqttClient = None
cli = None

#-------------------------------------------------------------
# MQTT stuff

# when connecting to mqtt do this;
def on_connect(client, userdata, flags, rc):
    logger.debug("Connected to MQTT with result code "+str(rc))
#    client.subscribe(sub_topic)

# when receiving a mqtt message do this;
def on_message(client, userdata, msg):
    message = str(msg.payload,'UTF-8')
    logger.debug("received message '%s' '%s'", msg.topic, message)

def on_publish(mosq, obj, mid):
    logger.debug("publish: " + str(mid))

#-------------------------------------------------------------
# signal handlers

def signal_handler(signal, frame):
    global stopped
    stopped = True

    if mqttClient is not None:
        mqttClient.loop_stop()

    if cli is not None:
        cli.close()

    sys.exit(0)


#-------------------------------------------------------------
# Telnet stuff

def connect_to_lms():
    global cli
    try:
        cli = telnetlib.Telnet(host=LMS_HOST, port=9090)
        cli.write("listen 1\n")
        logger.info("Connected to LMS")
    except:
        logger.warning("Error connecting to LMS")
        if (cli is not None): cli.close();
        cli = None


def read_lms():
    global cli
    if (cli is None):
        connect_to_lms()
    if (cli is not None):
        try:
            data = cli.read_until("\n")
            logger.debug("LMS data: "+data)
            return data
        except:
            cli.close()
            cli = None
            logger.warning("Error reading from LMS")
            return None
    else:
        logger.warning("Can't connect to LMS")
        return None

#=====================================================================
# ----- main ---------------------------------------------------------

# catch Ctrl-C etc, clean up on exit
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ----- setup MQTT -------------------------------------------
mqttClient = mqtt.Client(client_id=LMS_LOGNAME)
mqttClient.on_connect = on_connect
mqttClient.on_message = on_message
mqttClient.connect(MQTT_BROKER, 1883, 60)
mqttClient.loop_start()

# ----- setup Telnet connection to LMS --------------------------------
connect_to_lms()


# ----- forever loop
while (not stopped):
    time.sleep(0.1)

    data = read_lms()
    if (data is None):
        continue
    logger.debug("Data: " + data)
#    print "Data",data
    flds = data.strip().split(' ')
    if (len(flds)==0):
        continue
    if (flds[0] == 'listen'): 
        continue;
    uflds = [urllib.unquote(i) for i in flds]

    if (len(uflds)==5 and uflds[2]=='newsong'):
        continue
    if (len(uflds)>=3 and uflds[1]=='menustatus'):
        continue
    if (len(uflds)>2 and uflds[1]=='displaynotify'):
        continue

    if (len(uflds)>3 and uflds[1]=='playlist' and uflds[2]=='play'):
        topic = MQTT_PUB_BASE_LMS + uflds[0]+'/playlist/play/title'
        payload = uflds[4]
        if mqttClient is not None:
            mqttClient.publish( topic, payload )
        topic = MQTT_PUB_BASE_LMS + uflds[0]+'/playlist/play/item'
        payload = uflds[3]
    else:
        topic = MQTT_PUB_BASE_LMS + '/'.join(uflds[:-1])
        payload = uflds[-1]

    logger.debug("topic '%s' = '%s'" % (topic,payload))
    if mqttClient is not None:
        mqttClient.publish( topic, payload )


logger.info('terminating ...')

if mqttClient is not None:
    mqttClient.loop_stop()

if cli is not None:
    cli.close()

exit(0)

