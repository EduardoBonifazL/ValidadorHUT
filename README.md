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
* Instalar ***pandas***
* Instalar ***openpyxl***

### Descarga de archivos
* Ir a la carpeta *Resource*
* Entrar al link y descargar el excel de **Lideres Datio** y ponerlo en la carpeta *Resource*

### Configuración RunConfiguration
* Entrar a **Edit Configurations...**
* En **Use SDK of module** y seleccionar el SDK creado.
* En  **Environment variables** setear:
  * **HUT** = Poner la HUT a evaluar (*PAD3-XXXXX*)
  * **ProfileBBVA** = Colocar el Profile de Chrome asignado a la cuenta del BBVA (Pueden entrar en el navegador *chrome://version/* y ver **Ruta del perfil**)
  * **RutaUserData** = Debe estar la ruta de Chrome para los perfiles
  * Q = Entrar Al excel de **Lideres Datio** en la carpeta *Resource* y colocar el Nombre de la Pestaña del actual Q Ejemplo (Q3-23)
  
### Recomendaciones de Ejecución
* Cerrar todos los navegadores de Chrome y/o Chat Google antes de ejecutar.