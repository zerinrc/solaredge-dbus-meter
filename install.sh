#!/bin/bash

opkg update
opkg install python3-pip
pip3 install pyyaml
pip3 install solaredge_modbus

# set permissions for script files
chmod a+x /data/solaredge-dbus-meter/restart.sh
chmod 744 /data/solaredge-dbus-meter/restart.sh

chmod a+x /data/solaredge-dbus-meter/uninstall.sh
chmod 744 /data/solaredge-dbus-meter/uninstall.sh

chmod a+x /data/solaredge-dbus-meter/service/run
chmod 755 /data/solaredge-dbus-meter/service/run



# create sym-link to run script in deamon
ln -s /data/solaredge-dbus-meter/service /service/solaredge-dbus-meter



# add install-script to rc.local to be ready for firmware update
filename=/data/rcS.local
if [ ! -f $filename ]
then
    echo "entra"
    touch $filename
    chmod 755 $filename
    echo "#!/bin/bash" >> $filename
    echo >> $filename
fi

grep -qxF '/data/solaredge-dbus-meter/install.sh' $filename || echo '/data/solaredge-dbus-meter/install.sh' >> $filename
