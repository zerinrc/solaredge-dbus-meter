#!/bin/bash

rm /service/solaredge-dbus-meter
kill $(pgrep -f 'supervise solaredge-dbus-meter')
chmod a-x /data/solaredge-dbus-meter/service/run
./restart.sh
