====================================
MANUAL DE USUARIO - PERSON AUTOMATOR
====================================

1. DESCRIPCIÓN GENERAL
-----------------------
PERSON Automator es una aplicación diseñada para facilitar el envío de mensajes de WhatsApp de manera automatizada y programada, especialmente útil para negocios, recordatorios personales o atención al cliente.

2. REQUISITOS
-------------
- Tener WhatsApp Web iniciado en el navegador por defecto.
- Conexión a internet activa.
- Python 3.10+ instalado.
- Navegador compatible con WhatsApp Web.

3. INSTALACIÓN
--------------
1. Abre una terminal y ve a la carpeta donde descargaste la app.
2. Ejecuta `pip install -r requirements.txt`.
3. Ejecuta la app con `python automator.py`.

4. FUNCIONAMIENTO BÁSICO
-------------------------
- Al iniciar, la app carga la interfaz gráfica con Flet.
- Puedes ingresar el número de teléfono y el mensaje que deseas enviar.
- Puedes programar un horario específico para su envío.
- La app guarda automáticamente el historial en `send_history.json`.
- También puedes cargar configuraciones y programación desde JSON.

5. PROGRAMACIÓN DE MENSAJES
----------------------------
- La app permite programar mensajes para que se envíen automáticamente a ciertas horas usando el script `scheduler.py`.
- Para iniciar el programador: `python scheduler.py`.

6. NOTIFICACIONES
------------------
- Al enviarse un mensaje correctamente, recibirás una notificación de sistema (si el sistema operativo lo permite).

7. SEGURIDAD Y PRIVACIDAD
--------------------------
- No se almacena ni envía tu información personal.
- Toda la información se guarda localmente en archivos `.json`.

8. CIERRE DE LA APP
--------------------
- Puedes cerrar la app como cualquier ventana de escritorio.
- Se recomienda salir cerrando la ventana principal para asegurar que se guarden las configuraciones.

9. SOPORTE
----------
- Si encuentras errores, revisa los archivos `automator.log` o `scheduler.log`.

