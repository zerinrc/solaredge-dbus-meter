#!/usr/bin/env python

"""

opkg update
opkg install python3-pip
pip3 install pyyaml
pip3 install solaredge_modbus
"""

# import normal packages
import platform 
import logging
import sys
import os
import sys
if sys.version_info.major == 2:
    import gobject
else:
    from gi.repository import GLib as gobject
import sys
import time
import requests # for http GET
import configparser # for config/ini file


import dbus
import dbus.service


import solaredge_modbus

import paho.mqtt.client as mqtt
import yaml
import json

CFG_PATH='/data/solaredge-dbus-meter/config.yml'

with open(CFG_PATH, 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


# our own packages from victron
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '/opt/victronenergy/dbus-systemcalc-py/ext/velib_python'))
from vedbus import VeDbusService



class SystemBus(dbus.bus.BusConnection):
    def __new__(cls):
        return dbus.bus.BusConnection.__new__(cls, dbus.bus.BusConnection.TYPE_SYSTEM)

class SessionBus(dbus.bus.BusConnection):
    def __new__(cls):
        return dbus.bus.BusConnection.__new__(cls, dbus.bus.BusConnection.TYPE_SESSION)


def dbusconnection():
    return SessionBus() if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else SystemBus()


class DbusSolarEdgePVInverterService:
  def __init__(self, servicename, deviceinstance, paths, productname='SolarEdge PV Inv', connection='SolarEdge Inverter Modbus service'):


    self._meter = solaredge_modbus.Inverter(host=cfg['solaredge']['host'], port=cfg['solaredge']['port'])
    self._meter.connect()

    self._dbusservice = VeDbusService("{}.http_{:02d}".format(servicename, deviceinstance), dbusconnection())
    self._paths = paths
 
    logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))
 
    # Create the management objects, as specified in the ccgx dbus-api document
    self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
    self._dbusservice.add_path('/Mgmt/ProcessVersion', 'Unkown version, and running on Python ' + platform.python_version())
    self._dbusservice.add_path('/Mgmt/Connection', connection)
 
    # Create the mandatory objects
    self._dbusservice.add_path('/DeviceInstance', deviceinstance)
    #self._dbusservice.add_path('/ProductId', 16) # value used in ac_sensor_bridge.cpp of dbus-cgwacs
    #self._dbusservice.add_path('/ProductId', 0xFFFF) # id assigned by Victron Support from SDM630v2.py
    self._dbusservice.add_path('/ProductId', 9999) # found on https://www.sascha-curth.de/projekte/005_Color_Control_GX.html#experiment - should be an ET340 Engerie Meter
    self._dbusservice.add_path('/ProductName', productname)
    self._dbusservice.add_path('/CustomName', productname)    
    self._dbusservice.add_path('/Latency', None)    
    self._dbusservice.add_path('/FirmwareVersion', 0.1)
    self._dbusservice.add_path('/HardwareVersion', 0)
    self._dbusservice.add_path('/Connected', 1)
    #self._dbusservice.add_path('/Role', 'grid')
    self._dbusservice.add_path('/Position', 0) # normaly only needed for pvinverter
    self._dbusservice.add_path('/Serial', "implementar")
    self._dbusservice.add_path('/UpdateIndex', 0)
 
    # add path values to dbus
    for path, settings in self._paths.items():
      self._dbusservice.add_path(
        path, settings['initial'], gettextcallback=settings['textformat'], writeable=True, onchangecallback=self._handlechangedvalue)
 
    # last update
    self._lastUpdate = 0
 
    # add _update function 'timer'
    gobject.timeout_add(250, self._update) # pause 250ms before the next request
    
    self._meter.disconnect()
    # add _signOfLife 'timer' to get feedback in log every 5minutes
    #gobject.timeout_add(self._getSignOfLifeInterval()*60*1000, self._signOfLife)
 
 

 
 
  def _signOfLife(self):
    logging.info("--- Start: sign of life ---")
    logging.info("Last _update() call: %s" % (self._lastUpdate))
    logging.info("Last '/Ac/Power': %s" % (self._dbusservice['/Ac/Power']))
    logging.info("--- End: sign of life ---")
    return True
 
  def _update(self):   
    try:
       meter_data=self._meter.read_all()
       #send data to DBus
       self._dbusservice['/Ac/Power'] =  (meter_data['power_ac']*(10**meter_data['power_ac_scale']))
       self._dbusservice['/Ac/L1/Voltage'] = (meter_data['l1_voltage']*(10**meter_data['voltage_scale']))
       self._dbusservice['/Ac/L1/Current'] = (meter_data['l1_current']*(10**meter_data['current_scale']))
       self._dbusservice['/Ac/L1/Power'] =  (meter_data['power_ac']*(10**meter_data['power_ac_scale']))
       self._dbusservice['/Ac/L1/Energy/Forward'] = (meter_data['energy_total']*(10**meter_data['energy_total_scale']))/1000
       self._dbusservice['/Ac/Energy/Forward'] = (meter_data['energy_total']*(10**meter_data['energy_total_scale']))/1000
       
       # increment UpdateIndex - to show that new data is available
       index = self._dbusservice['/UpdateIndex'] + 1  # increment index
       if index > 255:   # maximum value of the index
         index = 0       # overflow from 255 to 0
       self._dbusservice['/UpdateIndex'] = index

       #update lastupdate vars
       self._lastUpdate = time.time()              
    except Exception as e:
       logging.critical('Error at %s', '_update', exc_info=e)
       
    # return true, otherwise add_timeout will be removed from GObject - see docs http://library.isr.ist.utl.pt/docs/pygtk2reference/gobject-functions.html#function-gobject--timeout-add
    return True
 
  def _handlechangedvalue(self, path, value):
    logging.debug("someone else updated %s to %s" % (path, value))
    return True # accept the change



#----------

class DbusSolarEdgeMeterService:
  def __init__(self, servicename, deviceinstance, paths, productname='SolarEdge Meter', connection='SolarEdge Meter Modbus service'):


    self._meter = solaredge_modbus.Meter(host=cfg['solaredge']['host'], port=cfg['solaredge']['port'])
    self._meter.connect()

    self._dbusservice = VeDbusService("{}.http_{:02d}".format(servicename, deviceinstance), dbusconnection())
    self._paths = paths
 
    logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))
 
    # Create the management objects, as specified in the ccgx dbus-api document
    self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
    self._dbusservice.add_path('/Mgmt/ProcessVersion', 'Unkown version, and running on Python ' + platform.python_version())
    self._dbusservice.add_path('/Mgmt/Connection', connection)
 
    # Create the mandatory objects
    self._dbusservice.add_path('/DeviceInstance', deviceinstance)
    #self._dbusservice.add_path('/ProductId', 16) # value used in ac_sensor_bridge.cpp of dbus-cgwacs
    #self._dbusservice.add_path('/ProductId', 0xFFFF) # id assigned by Victron Support from SDM630v2.py
    self._dbusservice.add_path('/ProductId', 45069) # found on https://www.sascha-curth.de/projekte/005_Color_Control_GX.html#experiment - should be an ET340 Engerie Meter
    self._dbusservice.add_path('/DeviceType', 345) # found on https://www.sascha-curth.de/projekte/005_Color_Control_GX.html#experiment - should be an ET340 Engerie Meter
    self._dbusservice.add_path('/ProductName', productname)
    self._dbusservice.add_path('/CustomName', productname)    
    self._dbusservice.add_path('/Latency', None)    
    self._dbusservice.add_path('/FirmwareVersion', 0.1)
    self._dbusservice.add_path('/HardwareVersion', 0)
    self._dbusservice.add_path('/Connected', 1)
    self._dbusservice.add_path('/Role', 'grid')
    self._dbusservice.add_path('/Position', 0) # normaly only needed for pvinverter
    self._dbusservice.add_path('/Serial', self._meter.read('c_serialnumber')['c_serialnumber'])
    self._dbusservice.add_path('/UpdateIndex', 0)
 
    # add path values to dbus
    for path, settings in self._paths.items():
      self._dbusservice.add_path(
        path, settings['initial'], gettextcallback=settings['textformat'], writeable=True, onchangecallback=self._handlechangedvalue)
 
    # last update
    self._lastUpdate = 0
 
    # add _update function 'timer'
    gobject.timeout_add(250, self._update) # pause 250ms before the next request
    
    self._meter.disconnect()

    # add _signOfLife 'timer' to get feedback in log every 5minutes
    #gobject.timeout_add(self._getSignOfLifeInterval()*60*1000, self._signOfLife)
 
 

 
 
  def _signOfLife(self):
    logging.info("--- Start: sign of life ---")
    logging.info("Last _update() call: %s" % (self._lastUpdate))
    logging.info("Last '/Ac/Power': %s" % (self._dbusservice['/Ac/Power']))
    logging.info("--- End: sign of life ---")
    return True
 
  def _update(self):   
    try:
       meter_data=self._meter.read_all()
       #send data to DBus
       self._dbusservice['/Ac/Power'] = -meter_data['power'] # positive: consumption, negative: feed into grid
       self._dbusservice['/Ac/L1/Voltage'] = (meter_data['l1n_voltage']*(10**meter_data['voltage_scale']))
       self._dbusservice['/Ac/L1/Current'] = (meter_data['l1_current']*(10**meter_data['current_scale']))
       self._dbusservice['/Ac/L1/Power'] = -(meter_data['l1_power']*(10**meter_data['power_scale']))
       self._dbusservice['/Ac/L1/Energy/Forward'] = (meter_data['l1_import_energy_active']*(10**meter_data['energy_active_scale']))/1000
       self._dbusservice['/Ac/L1/Energy/Reverse'] = (meter_data['l1_export_energy_active']*(10**meter_data['energy_active_scale']))/1000
       self._dbusservice['/Ac/Energy/Forward'] = self._dbusservice['/Ac/L1/Energy/Forward'] 
       self._dbusservice['/Ac/Energy/Reverse'] = self._dbusservice['/Ac/L1/Energy/Reverse'] 
       
       #logging
       logging.debug("House Consumption (/Ac/Power): %s" % (self._dbusservice['/Ac/Power']))
       logging.debug("House Forward (/Ac/Energy/Forward): %s" % (self._dbusservice['/Ac/Energy/Forward']))
       logging.debug("House Reverse (/Ac/Energy/Revers): %s" % (self._dbusservice['/Ac/Energy/Reverse']))
       logging.debug("---");
       
       # increment UpdateIndex - to show that new data is available
       index = self._dbusservice['/UpdateIndex'] + 1  # increment index
       if index > 255:   # maximum value of the index
         index = 0       # overflow from 255 to 0
       self._dbusservice['/UpdateIndex'] = index

       #update lastupdate vars
       self._lastUpdate = time.time()              
    except Exception as e:
       logging.critical('Error at %s', '_update', exc_info=e)
       
    # return true, otherwise add_timeout will be removed from GObject - see docs http://library.isr.ist.utl.pt/docs/pygtk2reference/gobject-functions.html#function-gobject--timeout-add
    return True
 
  def _handlechangedvalue(self, path, value):
    logging.debug("someone else updated %s to %s" % (path, value))
    return True # accept the change
 


def main():
  #configure logging
  logging.basicConfig(      format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO,
                            handlers=[
                                logging.FileHandler("%s/current.log" % (os.path.dirname(os.path.realpath(__file__)))),
                                logging.StreamHandler()
                            ])
 
  try:
      logging.info("Start");
  
      from dbus.mainloop.glib import DBusGMainLoop
      # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
      DBusGMainLoop(set_as_default=True)
     
      #formatting 
      _kwh = lambda p, v: (str(round(v, 2)) + ' KWh')
      _a = lambda p, v: (str(round(v, 1)) + ' A')
      _w = lambda p, v: (str(round(v, 1)) + ' W')
      _v = lambda p, v: (str(round(v, 1)) + ' V')   
     
      #start our main-service
      pvac_output = DbusSolarEdgeMeterService(
        servicename='com.victronenergy.grid',
        deviceinstance=40,
        paths={
          '/Ac/Energy/Forward': {'initial': 0, 'textformat': _kwh}, # energy bought from the grid
          '/Ac/Energy/Reverse': {'initial': 0, 'textformat': _kwh}, # energy sold to the grid
          '/Ac/Power': {'initial': 0, 'textformat': _w},
          
          '/Ac/Current': {'initial': 0, 'textformat': _a},
          '/Ac/Voltage': {'initial': 0, 'textformat': _v},
          
          '/Ac/L1/Voltage': {'initial': 0, 'textformat': _v},
          '/Ac/L1/Current': {'initial': 0, 'textformat': _a},
          '/Ac/L1/Power': {'initial': 0, 'textformat': _w},
          '/Ac/L1/Energy/Forward': {'initial': 0, 'textformat': _kwh},
          '/Ac/L1/Energy/Reverse': {'initial': 0, 'textformat': _kwh},
        })


      pvac_output = DbusSolarEdgePVInverterService(
        servicename='com.victronenergy.pvinverter',
        deviceinstance=41,
        paths={
          '/Ac/Energy/Forward': {'initial': 0, 'textformat': _kwh}, # energy bought from the grid
          '/Ac/Power': {'initial': 0, 'textformat': _w},
          
          '/Ac/Current': {'initial': 0, 'textformat': _a},
          '/Ac/Voltage': {'initial': 0, 'textformat': _v},
          
          '/Ac/L1/Voltage': {'initial': 0, 'textformat': _v},
          '/Ac/L1/Current': {'initial': 0, 'textformat': _a},
          '/Ac/L1/Power': {'initial': 0, 'textformat': _w},
          '/Ac/L1/Energy/Forward': {'initial': 0, 'textformat': _kwh},
        })

     
      logging.info('Connected to dbus, and switching over to gobject.MainLoop() (= event based)')
      mainloop = gobject.MainLoop()
      mainloop.run()            
  except Exception as e:
    logging.critical('Error at %s', 'main', exc_info=e)
if __name__ == "__main__":
  main()