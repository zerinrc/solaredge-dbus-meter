## Integración de SolarEdge con Victron
### Declinación de responsabilidad.
Tanto el proyecto de software, como esta guia son con fines educativos y en ningun caso debe utilizarse en un entorno de producción real.
El autor no se responsabiliza en ningun caso, de posibles daños ocasionados sobre ningun hardware, software, bienes, configuración, etc, ni de daños personales, por el uso de este software o guia.


### Habilitar Modbus TCP en SolarEdge
Si no disponemos de cuenta de instalador o setApp, podemos acceder directamnte a la configuración del inversor creando una red wifi local. Para ello:
- Mover palanca roja a la izquierda (posición P un par de segundos)
- conectar a la red wifi que crea el inversor. La password está en el lateral derecho junto a un QR
- una vez conectados a la wifi del inversor acceder con un navegador a la dirección http://172.16.0.1
- la wifi que crea se cierra sola cuando pasa un tiempo sin un cliente conectado y hay que volver a empezar en caso necesario

Una vez dentro de la aplicacion web, hay que habilitar el Modbus TCP en el apartado de Comunicaciones>Modbus TCP port>Habilitar>Puerto 502 (por defecto viene 1502, puede usarse cualquiera de ellos, pero para conectarnos a el, luego habrá que especificar el mismo puerto)

Es recomendable asignar una IP fija dentro del apartado de comunicaciones, o bien reservar una en el DHCP de nuestra red local.

### Habilitar SSH en Venus OS
Configuracion>General>Nivel de acceso

Pulsar cinco segundos flecha derecha hasta que aparezca la opcion de introducir password

Introducir nueva contraseña para root

Activar ssh en lan


1. General

![Configuracion General](https://github.com/zerinrc/solaredge-dbus-meter/raw/main/img/ssh_sp_02.png)

2. Nivel de acceso

![Nivel de acceso](https://github.com/zerinrc/solaredge-dbus-meter/raw/main/img/ssh_sp_03.png)

3. Pulsar 5 segundos la flecha derecha

![Pulsar 5 segundos la flecha derecha](https://github.com/zerinrc/solaredge-dbus-meter/raw/main/img/ssh_sp_04.png)

4. En Set root password introducir la contraseña para root que deseemos.

![Tile Overview](https://github.com/zerinrc/solaredge-dbus-meter/raw/main/img/ssh_sp_05.png)

![Tile Overview](https://github.com/zerinrc/solaredge-dbus-meter/raw/main/img/ssh_sp_06.png)

5. Activar SSH en LAN

![Tile Overview](https://github.com/zerinrc/solaredge-dbus-meter/raw/main/img/ssh_sp_07.png)


Ahora ya podemos acceder por SSH con el usuario root y la password introducida en el paso 5.

### Instalación del conector en el dispositivo Venus
Accederemos por SSH con el usuario root y la password fijada anteriormente en el paso 5, y ejecutaremos el siguiente comando:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/zerinrc/solaredge-dbus-meter/main/installfromscratch.sh)"
```

Editar fichero config.yml con los parametros de nuestro inversor solar edge

Reiniciar dispositivo Venus haciendo
```
# reboot
```

