wget https://github.com/zerinrc/solaredge-dbus-meter/archive/refs/heads/main.zip
unzip main.zip "solaredge-dbus-meter-main/*" -d /data
mv /data/solaredge-dbus-meter-main /data/solaredge-dbus-meter
chmod a+x /data/solaredge-dbus-meter/install.sh
/data/solaredge-dbus-meter/install.sh
rm main.zip
