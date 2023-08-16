from Code.Clases import ValidHut
from Code.Funciones import init_driver, validador
import time

driver = init_driver()
time.sleep(1)

if driver.title == "BBVA":
    print("Favor de iniciar sesión del BBVA en Chrome")
    time.sleep(5)
    exit()

Historia = ValidHut(driver)
validador(Historia)
