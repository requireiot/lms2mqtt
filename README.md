lms2mqtt
====
convert notifications from Logitech Media Server to MQTT messages

## Objective
Publish status changes such as "song started playing" or "alarm went off" as MQTT messages, for use by home automation controllers, such as openHAB.

## Prerequisites
* [Logitech Media Server](https://wiki.slimdevices.com/index.php/Logitech_Media_Server.html) (LMS), obviously, running on the same or a different machine, reachable via *servername*:9090
* an MQTT broker such as [mosquitto](https://mosquitto.org/).
* a Linux machine (real or virtual) that can run the daemon script `lms2mqtt.py`. I use Debian 10 on a virtual machine

## Installation
* copy `lms2mqtt.py`to a directory of your choice, mine is in `/home/admin/daemons/lms2mqtt`
* configure the name of the machien running the LMS server in `lms2mqtt.py`
* configure the name of the machine running the MQTT broker in `lms2mqtt.py`
* copy file `bw-lms2mqtt` to `/etc/init.d/` and make it executable
* in `bw-lms2mqtt`, set the path where you stored the `lms2mqtt.py` script 
* activate the service with `sudo update-rc.d bw-lms2mqtt defaults`
* start the service with `sudo service bw-lms2mqtt start`

## Troubleshooting
I have noticed that the daemon sometimes looses connection with LMS, don't quite understand why. As a dirty fix, I created a script `/root/restart-lms2mqtt.sh` that contains
```shell
#!/bin/bash
service bw-lms2mqtt stop
sleep 15
service bw-lms2mqtt start
```
I run this one every night, via this crontab entry
```
0 1 * * * /root/restart-lms2mqtt.sh
```
