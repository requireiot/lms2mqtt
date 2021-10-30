__lms2mqtt daemon__
___

- [Objectives](#objectives)
- [Requirements](#requirements)
  - [Connectivity](#connectivity)
  - [Debugging](#debugging)
  - [Configuration](#configuration)
  - [Reporting](#reporting)

Notation:
- [x] requirement is implemented and tested. 
- [ ] requirement is not implemented or tested, ideas for future versions.

---
## Objectives
* use information about Logitech Media Player (LMS) and connected players in home automation applications
* in particular, support defiition of home automation actions in response to events related to SqueezeBox alarms (alarm starts, snooze, alarm off)
* explore what information is made available by LMS Telnet interface

## Requirements

### Connectivity
- [x] `R01.01` connect to LMS via Telnet interface to retrieve status information
- [x] `R01.02` connect to MQTT broker, to publish notifications about LMS events

### Debugging
- [x] `R02.01` ability to run daemon from the command line, and end gracefully when Ctrl-C is pressed
- [x] `R02.02` when run from command line, show all communication from LMS

### Configuration
- [x] `R03.01` name of host running LMS is configurable, in source code
- [x] `R03.02` name of host running MQTT broker is configurable, in source code
- [x] `R03.03` configuration items common to multiple daemons (e.g. MQTT host) are configurable in *one* place

### Reporting
- [x] report information re playlists and start/stop playing
- [x] report information re volume changes
- [x] report information re power on/off
- [x] report information re alarms
- [x] do not report information re menu navigation on SqueezeBox
- [x] do not report information re display updates on SqueezeBox