# Validador HUT
### Configuración de Entorno
* Descargar o clonar el repositorio
* Descomprimir **ValidadorHUT.zip** para extraer la carpeta **.idea** y **ValidadorHUT.lml**
* Abrir el repositorio en IntelliJ
* Entrar a File / Project Structure... (Ctrl + Alt + Mayús + S)
* Entrar Project Setting / Project / SDK
* Add SDK / Python SDK... (Crear SDK)
* Entrar a Project Setting / Module / ValidadorHUT / Module SDK (Seleccionar el SDK creado)
* Instalar ***selenium***
* Instalar ***pyhocon***

### Configuración RunConfiguration
* Entrar a **Edit Configurations...**
* En **Use SDK of module** y seleccionar el SDK creado.
* En  **Environment variables** setear:
  * **HUT** = Poner la HUT a evaluar (*PAD3-XXXXX*)
  * **ProfileBBVA** = Colocar el Profile de Chrome asignado a la cuenta del BBVA (Pueden entrar en el navegador *chrome://version/* y ver **Ruta del perfil**)
  * **RutaUserData** = Debe estar la ruta de Chrome para los perfiles
  
### Recomendaciones de Ejecución
* Cerrar todos los navegadores de Chrome y/o Chat Google antes de ejecutar.