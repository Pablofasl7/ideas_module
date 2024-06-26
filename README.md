# Módulo sobre la gestión de ideas

Este módulo de Odoo permite gestionar ideas dentro de tu empresa, permitiendo a los usuarios proponer nuevas ideas, votar por ellas y llevar un seguimiento del estado de cada idea.

## Características

- Creación y gestión de ideas.
- Votación por parte de los usuarios.
- Seguimiento del estado de cada idea (en revisión, aprobada, en proceso, completada, cancelada).
- Asignación de responsables a cada idea.
- Generación de informes de ideas.

## Instalación

1. Clona este repositorio en tu servidor Odoo:

    git clone https://github.com/Pablofasl7/ideas_module.git

2. Reinicia el servidor Odoo para cargar el nuevo módulo.

3. Ve a la lista de aplicaciones de Odoo y busca el módulo "ideas_module" para poder activarlo.

## Configuración de Permisos

Para que el módulo funcione correctamente y los usuarios tengan los permisos necesarios, debemos de configurar los permisos de usuario. 

1. Ve a los ajustes de usuarios en Odoo.
2. Para cada usuario, asigna los permisos adecuados según el rol que deben desempeñar:
    - **User**: Permite a los usuarios votar por las ideas aprobadas.
    - **Manager**: Permite a los administradores aprobar ideas y votar.
    - **Acceso para votar de los usuarios**: Permite a los usuarios votar en las ideas.
    - **Acceso para votar de los managers**: Permite a los administradores votar y gestionar votos en las ideas.

## Uso

1. Ve al menú "Idea" en Odoo.
2. Desde aquí podrás crear nuevas ideas, votar por ideas existentes, y cambiar el estado de las ideas según avancen.
3. Puedes generar informes de las ideas para tener una visión general de todas las propuestas y su estado.
   
## Créditos

Este módulo fue desarrollado por Pablo Marín - (https://github.com/Pablofasl7).

## Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](LICENSE).

## Para mas información, ver el siguiente vídeo demostrativo
https://youtu.be/Xxkq3SI_DvU

##  Memoria del proyecto
https://github.com/Pablofasl7/ideas_module/blob/main/Proyecto%20Final%20TFG%20-%20Pablo%20Marin.pdf
