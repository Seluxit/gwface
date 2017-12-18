# Gateway interface changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [0.3.0] - 2017-12-18
### Added

Client functionality:
- INCLUDE device if it is not included
- DELETE device sending 'DELETE' request or 'PUT' request by setting 'included':'0' in the data

Gateway:
- DELETE device. Sending notification to all interfaces.

### Fix
- Value timestamp format in milliseconds. 

## [0.2.0] - 2017-12-06
### Added

Client functionality:
- GET gateway
- GET configurations, partners, actions, calendars, calculations, timers, statemachines as list
- GET specified configuration, partner, action, calendar, calculation, timer, statemachine

Gateway:
- POST configurations, partners, actions, calendars, calculations, timers, statemachines
- POST device status

## [0.1.0] - 2017-12-01
### Added

Client functionality:
- GET all (network, devices, services and values at the same time) 
- GET specified network, device, service, value.
- GET specified network, device, service, value *list*.
- PUT value

Gateway 
- POST and PUT network, device, service and values


### Communication protocol
- jsonRPC [specification](http://www.jsonrpc.org/specification).

### Data structure 
+ gateway
+ network
  + device
      + status
      + service
          + value
      + configuration
          + partner
          + action
          + calendar
          + calculation
          + timer
          + statemachine

