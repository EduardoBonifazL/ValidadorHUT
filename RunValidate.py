from Code.Clases import *
from Code.Funciones import validador
import time

driver = init_driver()
time.sleep(1)

if driver.title == "BBVA":
    print("Favor de iniciar sesión del BBVA en Chrome")
    time.sleep(5)
    exit()

Historia = ValidHut(driver)
validador(Historia)
