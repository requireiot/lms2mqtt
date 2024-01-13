lms2mqtt
====
convert notifications from Logitech Media Server to MQTT messages

## Objective
Publish Logitech Media Server (LMS) status changes such as "song started playing" or "alarm went off" as MQTT messages, for use by home automation controllers, such as openHAB.

## Prerequisites
* [Logitech Media Server](https://wiki.slimdevices.com/index.php/Logitech_Media_Server.html) (LMS), obviously, running on the same or a different machine, reachable via *servername*:9090
* an MQTT broker such as [mosquitto](https://mosquitto.org/).
* a Linux machine (real or virtual) that can run the daemon script `lms2mqtt.py`. I use Debian 10 on a virtual machine
* a recent Python 3 version
* the Eclipse MQTT library, say `pip3 install paho-mqtt`

## Installation
* copy `lms2mqtt.py`to a directory of your choice, mine is in `/home/admin/daemons/lms2mqtt`
* configure the name of the machine running the LMS server in `lms2mqtt.py`
* configure the name of the machine running the MQTT broker in `lms2mqtt.py`
* configure the portnumber of the MQTT broker in `lms2mqtt.py`
* configure the username for the MQTT broker in `lms2mqtt.py`
* configure the password for the MQTT broker in `lms2mqtt.py`
* if no username or password is used comment out line 149: `mqttclient.username_pw_set(MQTT_USER, MQTT_PASSWD)` in `lms2mqtt.py`
<br/>

* when using systemd:
* as root or using sudo: create a file `/etc/systemd/system/lms2mqtt.service` and insert:
```
[Unit]
Description=MQTT for the Logitech Media Server
After=multi-user.target

[Service]
WorkingDirectory=/home/<user>/
User=<user>
ExecStart=/usr/bin/python3 /home/<user>/<path-to-lms2mqtt>/lms2mqtt.py
Type=simple

[Install]
WantedBy=multi-user.target
```
* change `<user>` to the user you are using in this case: `admin`
* change `<path-to-lms2mqtt>` to the directory where your `lms2mqtt.py` is, in this case: `daemons/lms2mqtt`
* as root or using sudo reload systemd: `sudo systemctl daemon-reload`
* then start lms2mqtt: `sudo systemctl start lms2mqtt.service`
* then make it start at boot: `sudo systemctl enable lms2mqtt.service`
<br/>

* when using init.d:
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

## MQTT messages
All MQTT messages start with `lms/`, then the MAC address of the player, then a path that is the combination of all the notification words sent by LMS. The payload is the last part of the notification.

Notifications related to display updates and navigation through the SqueezeBox menus are suppressed, because I assume that's not relevant for home automation purposes.

### Example

Here is an example, a series of MQTT messages as I operate a SqueezeBox player:

Turn on the player
```
lms/b8:27:eb:fe:f8:9d/prefset/server/power 1
```
Select a folder and start playing
```
lms/b8:27:eb:fe:f8:9d/playlistcontrol/cmd:load/folder_id:14186 count:1
lms/b8:27:eb:fe:f8:9d/playlist/load /storage/music/@Classical/Maria Callas/La Divina I
lms/b8:27:eb:fe:f8:9d/playlist stop
lms/b8:27:eb:fe:f8:9d/playlist/jump/0/ 0
lms/b8:27:eb:fe:f8:9d/playlist/open file:///storage/music/@Classical/Maria%20Callas/La%20Divina%20I/01%20Un%20bel%20d%C3%AC,%20vedremo%20(Madama%20Butterfly%20-%20Puccini).mp3
lms/b8:27:eb:fe:f8:9d/playlist/open file:///storage/music/@Classical/Maria%20Callas/La%20Divina%20I/01%20Un%20bel%20d%C3%AC,%20vedremo%20(Madama%20Butterfly%20-%20Puccini).mp3
lms/b8:27:eb:fe:f8:9d/playlist load_done
```
Turn up the volume 3 times
```
lms/b8:27:eb:fe:f8:9d/mixer/volume +2
lms/b8:27:eb:fe:f8:9d/prefset/server/volume 50
lms/b8:27:eb:fe:f8:9d/mixer/volume +2
lms/b8:27:eb:fe:f8:9d/prefset/server/volume 52
lms/b8:27:eb:fe:f8:9d/mixer/volume +2
lms/b8:27:eb:fe:f8:9d/prefset/server/volume 54
```
Pause the player
```
lms/b8:27:eb:fe:f8:9d pause
lms/b8:27:eb:fe:f8:9d/playlist/pause 1
```
Play an internet radio station
```
lms/b8:27:eb:fe:f8:9d/playlist/play/item http://stream.srg-ssr.ch/m/rsj/aacp_96
lms/b8:27:eb:fe:f8:9d/playlist stop
lms/b8:27:eb:fe:f8:9d/playlist/jump/0/ 0
lms/b8:27:eb:fe:f8:9d/playlist load_done
lms/b8:27:eb:fe:f8:9d/playlist/open http://stream.srg-ssr.ch/m/rsj/aacp_96
lms/b8:27:eb:fe:f8:9d/playlist/newsong In Mission Of Tradition - The Pink Panther Theme
```
Turn off power
```
lms/b8:27:eb:fe:f8:9d/power 0
lms/b8:27:eb:fe:f8:9d/prefset/server playingAtPowerOff
lms/b8:27:eb:fe:f8:9d/prefset/server/power 0
```
