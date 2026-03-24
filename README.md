# Diagnóstico de Ingeniería de Datos: GitHub Repo Miner & Visualizer

Este proyecto implementa una arquitectura basada en patrón Productor-Consumidor para extraer, procesar y visualizar en tiempo real las convenciones de nombres más utilizadas en repositorios públicos de Python y Java alojados en GitHub

## Requisitos Previos

Para ejecutar este proyecto, su máquina debe tener Docker Desktop instalado y corriendo

## Configuración Inicial 

Antes de levantar el proyecto, es necesario configurar el Token de Acceso Personal de GitHub para evitar los límites de peticiones anónimas (Rate Limit).

1. Ir a https://github.com/settings/tokens
2. Clic en Generate new token (classic)
3. Darle un titulo 
4. No marcar ninguna casilla
5. Clic en Generate token al fondo
6. Copiar el token generado 
7. Editar el archivo `miner/.env` y pegar el token clásico de GitHub:

## Ejecución del Proyecto
Abra una terminal en la raíz del proyecto (donde se encuentra el archivo docker-compose.yml).
Ejecute el siguiente comando para construir las imágenes y levantar toda la infraestructura:
docker-compose up --build

## Uso del Panel Web (Dashboard)
Una vez que los contenedores estén corriendo y el Miner comience a enviar datos:
Abra su navegador web de preferencia.
Diríjase a la siguiente dirección local: http://localhost:8501
En la interfaz, haga clic en el botón "Actualizar Datos"
El consumidor extraerá todos los mensajes pendientes en Redis y actualizará los gráficos de barras interactivos con el Top 10 actualizado de Java y Python.

## Detención del Sistema
Para detener la minería y apagar los servidores de forma limpia y segura, siga estos pasos:

Vuelva a la terminal donde ejecutó el proyecto y presione Ctrl + C para detener los procesos en vivo (Graceful stop)
Para destruir los contenedores y liberar la red virtual creada, ejecute:
docker-compose down