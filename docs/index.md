## Integración de SolarEdge con Victron
### Declinación de responsabilidad.
Tanto el proyecto de software, como esta guia son con fines educativos y en ningun caso debe utilizarse en un entorno de producción real.
El autor no se responsabiliza en ningun caso, de posibles daños ocasionados sobre ningun hardware, software, bienes, configuración, etc, ni de daños personales, por el uso de este software o guia.


### Habilitar Modbus TCP en SolarEdge
Habilitar Modbus tcp en solaredge, y asignar IP fija o reservar en el DHCP.

### Habilitar SSH en Venus OS
Obtener root en el dispositivo venus (cerbo, color control, rasperry... etc)
Configuracion>General>Nivel de acceso
Pulsar cinco segundos flecha derecha hasta que aparezca la opcion de introducir password
Introducir nueva contraseña para root
Activar ssh en lan

Acceder por ssh como root y la password previamente introducida en el dispositivo Venus.

### Instalación del conector en el dispositivo Venus
Instalar el software desde el repositorio de GitHub, introduciendo la siguiente secuencia de comandos:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/zerinrc/solaredge-dbus-meter/main/installfromscratch.sh)"
```

Editar fichero config.yml con los parametros de nuestro inversor solar edge
Reiniciar dispositivo Venus



Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [Basic writing and formatting syntax](https://docs.github.com/en/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/zerinrc/solaredge-dbus-meter/settings/pages). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://docs.github.com/categories/github-pages-basics/) or [contact support](https://support.github.com/contact) and we’ll help you sort it out.