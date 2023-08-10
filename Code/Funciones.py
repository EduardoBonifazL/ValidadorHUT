from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import os


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={os.environ["RutaUserData"]}')
    options.add_argument(f'--profile-directory={os.environ["ProfileBBVA"]}')
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.maximize_window()
    driver.get('https://www.google.com')
    driver.get(f'https://jira.globaldevtools.bbva.com/browse/{os.environ["HUT"]}')
    print(f'Evaluando HUT: {os.environ["HUT"]}')
    return driver


def get_value(driver, xpath: str, t=1):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        return driver.find_element(By.XPATH, xpath).text
    except:
        return


def get_list(driver, xpath: str, t=1, text=True):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        xpath_list = driver.find_elements(By.XPATH, xpath)
        if text:
            return list(map(lambda x: x.text, xpath_list))
        else:
            return xpath_list
    except:
        return


def get_attribute(driver, xpath: str, attribute: str, t=1):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        return driver.find_element(By.XPATH, xpath).get_attribute(attribute)
    except:
        return


def get_value_link(driver, xpath: str, t=1):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        return [get_value(driver, xpath, 1), get_attribute(driver, xpath, "href")]
    except:
        return


def get_sub_task(driver, t=1):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((
            By.XPATH, '//*[@data-content="subtasks"]')))
        rows = driver.find_elements(By.XPATH, '//*[@data-content="subtasks"]/table/tbody/tr')
        sub_task = []
        for row in rows:
            sub_task.append(
                [row.find_element(By.XPATH, 'td[@class="stsummary"]').text,
                 get_attribute(row, 'td[@class="stsummary"]/a', "href"),
                 row.find_element(By.XPATH, 'td[@class="status"]').text,
                 row.find_element(By.XPATH, 'td[@class="assignee"]').text]
            )
        return sub_task
    except:
        return


def get_child_item(driver, t=1):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((
            By.XPATH, '//dt[@title="is child item of"]/following-sibling::dd/div[@class="link-content"]')))
        rows = driver.find_elements(
            By.XPATH, '//dt[@title="is child item of"]/following-sibling::dd/div[@class="link-content"]')
        child_item = []
        for row in rows:
            child_item.append(
                [row.find_element(By.XPATH, 'p/span/a').text,
                 get_attribute(row, 'p/span/a', "href"),
                 row.find_element(By.XPATH, 'p/span/span').text,
                 row.find_element(By.XPATH, 'ul/li[@class="status"]').text]
            )
        return child_item
    except:
        return


def get_user_approved(driver, t=1):
    usuarios = get_list(
        driver,
        '//div[@class="activity-item approved-activity" or @class="activity-item unapproved-activity" or @class="activity-item reviewed-activity"]//span[@class="user-name"]',
        t
    )
    estados = get_list(
        driver,
        '//div[@class="activity-item approved-activity" or @class="activity-item unapproved-activity" or @class="activity-item reviewed-activity"]//span[@class="lozenge-wrapper"]',
    )
    user_reviewers = dict()
    if (usuarios is not None) and (estados is not None):
        for usuario, estado in zip(reversed(usuarios), reversed(estados)):
            if estado == "APPROVED":
                user_reviewers[usuario] = True
            else:
                user_reviewers[usuario] = False
        return [clave for clave, valor in user_reviewers.items() if valor]
    else:
        return


def get_files(driver, t=1):
    path_file = dict()
    folder_closed = get_list(driver, '//span[@class="aui-icon aui-icon-small icon-folder-closed directory-icon"]', t, False)
    while folder_closed is not None:
        for folder in folder_closed:
            folder.click()
        folder_closed = get_list(driver, '//span[@class="aui-icon aui-icon-small icon-folder-closed directory-icon"]', text=False)
    file_list = get_list(driver, '//a[span[@class="aui-icon aui-icon-small icon-file-added status-icon" or @class="aui-icon aui-icon-small icon-file-moved status-icon" or @class="aui-icon aui-icon-small icon-file-modified status-icon" or @class="aui-icon aui-icon-small icon-file-copied status-icon"]]', text=False)
    file_link = []
    for file in file_list:
        name = file.text
        for i in ['.conf', '.json', '.schema', '.feature', '.scala']:
            if i in name:
                file.click()
                file_segment = get_value(driver, '//span[@class="file-breadcrumbs-segment-highlighted"]')
                while name != file_segment:
                    file_segment = get_value(driver, '//span[@class="file-breadcrumbs-segment-highlighted"]')
                file_link.append(get_attribute(driver, '//a[@aria-label="View the entire source for this file"]', 'href').replace('/browse/', '/raw/'))
    for link in file_link:
        driver.get(link)
        path = link.split('?at=')[0]
        path_file[path] = get_value(driver, '/html/body/pre', 4)
    return path_file


# Funciones de Validación:
def valid_find_hut(summary):
    # Falta implementar malla
    estado = "FAILURE"
    comentario = ""
    tipo = ""
    if summary is not None:
        lista_hut = [
            ' ingesta ', ' hammurabi ', ' procesamiento ', ' smartcleaner ', ' operativización ', ' migrationTool '
        ]
        if "Control M" in summary:
            tipo = "Control M"
            comentario = f", se encontró {tipo.upper()}"
            estado = "OK"
        else:
            for i in lista_hut:
                if i in summary.lower():
                    tipo = i.strip()
                    comentario = f", se encontró {tipo.upper()}"
                    estado = "OK"
                    break

    print(f"* Tipo de la HUT{comentario}: {estado}")
    return tipo


def valid_key_val(key_val):
    estado = "FAILURE"
    if key_val is not None:
        if "PAD3" == key_val[: 4]:
            estado = "OK"
    print(f"* Debe ser PAD3: {estado}")


def valid_type(type_hut, type_hut_value: str):
    estado = "FAILURE"
    if type_hut == type_hut_value:
        comentario = f'Se encontró tipo "{type_hut}"'
        estado = "OK"
    else:
        comentario = f'Se encontró tipo "{type_hut}", se esperaba "{type_hut_value}"'
    print(f'* {comentario}: {estado}')


def valid_acceptance_criteria(acceptance_criteria, acceptance_criteria_value: str):
    estado = "FAILURE"
    if acceptance_criteria is not None:
        if acceptance_criteria == acceptance_criteria_value:
            comentario = f'Criterio de Aceptación "{acceptance_criteria}"'
            estado = "OK"
        else:
            comentario = f'Se encontró Criterio de Aceptación "{acceptance_criteria}", se esperaba "{acceptance_criteria_value}"'
        print(f'* {comentario}: {estado}')
    else:
        print(f'* No se encontró Criterio de Aceptación: {estado}')


def valid_status(status, status_value: str):
    estado = "FAILURE"
    if status == status_value:
        comentario = f'HUT en estado "{status}"'
        estado = "OK"
    else:
        comentario = f'Se encontró HUT en estado "{status}", se esperaba "{status_value}"'
    print(f'* {comentario}: {estado}')


def valid_item_type(item_type, item_type_value: str):
    estado = "FAILURE"
    if item_type == item_type_value:
        comentario = f'Item Type "{item_type}"'
        estado = "OK"
    else:
        comentario = f'Se encontró Item Type  "{item_type}", se esperaba "{item_type_value}"'
    print(f'* {comentario}: {estado}')


def valid_tech_stack(tech_stack, tech_stack_value: str):
    estado = "FAILURE"
    if tech_stack == tech_stack_value:
        comentario = f'Tech Stack "{tech_stack}"'
        estado = "OK"
    else:
        comentario = f'Se encontró Tech Stack "{tech_stack}", se esperaba "{tech_stack_value}"'
    print(f'* {comentario}: {estado}')


def valid_label(labels: list, label_list: list):
    estado = "FAILURE"
    if labels is not None:
        for label in label_list:
            if label in labels:
                comentario = f'Se encontró label "{label}"'
                estado = "OK"
            else:
                comentario = f'Se esperaba label "{label}"'
                estado = "FAILURE"
            print(f'* {comentario}: {estado}')
    else:
        print(f'* Se esperaba labels {label_list}: {estado}')


def valid_sub_tasks(sub_tasks: list, tarea, status, asignado_text, asignado):
    estado = "FAILURE"
    if sub_tasks is not None:
        for sub_task in sub_tasks:
            if tarea == sub_task[0]:
                if status == sub_task[2]:
                    comentario = f'Subtarea {tarea} {status}'
                    estado = "OK"
                else:
                    comentario = f'Subtarea {tarea} {sub_task[2]} se esperaba {status}'
                    estado = "FAILURE"
                print(f'* {comentario}: {estado}')
                if asignado == sub_task[3]:
                    comentario = f'Subtarea {tarea} {asignado_text}'
                    estado = "OK"
                else:
                    comentario = f'Subtarea {tarea} asignado {sub_task[3]} se esperaba {asignado}'
                    estado = "FAILURE"
                print(f'* {comentario}: {estado}')
                break
    else:
        print(f'* Se esperaba documento {tarea}: {estado}')


def ingesta(clase):
    valid_type(clase.Type, "Story")
    valid_label(clase.Labels, ['ReleasePRDatio'])
    valid_acceptance_criteria(clase.AcceptanceCriteria, "Desarrollo según los Lineamientos del Equipo de DQA.")
    valid_status(clase.Status, "READY")
    valid_item_type(clase.ItemType, "Technical")
    valid_tech_stack(clase.TechStack, "Data - Dataproc")
    valid_sub_tasks(clase.SubTask, "[C204][QA]", "READY", "sin asignar", "Unassigned")
    valid_sub_tasks(clase.SubTask, "[C204][PO]", "ACCEPTED", "asignado a PO", "")  # Falta implementar verificación de PO


def hammurabi(clase):
    valid_type(clase.Type, "Story")
    valid_label(clase.Labels, ['ReleasePRDatio'])
    valid_acceptance_criteria(clase.AcceptanceCriteria, "Desarrollo según los Lineamientos del Equipo de DQA.")
    valid_status(clase.Status, "READY")
    valid_item_type(clase.ItemType, "Technical")
    valid_tech_stack(clase.TechStack, "Data - Dataproc")
    valid_sub_tasks(clase.SubTask, "[C204][QA]", "READY", "sin asignar", "Unassigned")
    valid_sub_tasks(clase.SubTask, "[C204][PO]", "ACCEPTED", "asignado a PO", "")  # Falta implementar verificación de PO


def malla(clase):
    valid_type(clase.Type, "Dependency")
    valid_label(clase.Labels, ['release', 'ReleaseMallasDatio'])
    valid_status(clase.Status, "READY")
    valid_item_type(clase.ItemType, "Technical")
    valid_tech_stack(clase.TechStack, "Data - Dataproc")
    valid_sub_tasks(clase.SubTask, "[C204][QA]", "READY", "sin asignar", "Unassigned")
    valid_sub_tasks(clase.SubTask, "[C204][PO]", "ACCEPTED", "asignado a PO", "")  # Falta implementar verificación de PO
    valid_sub_tasks(clase.SubTask, "[P110][AT]", "ACCEPTED", "asignado a SM", "")  # Falta implementar verificación de SM


def validador(clase):
    tipo_hut = valid_find_hut(clase.Summary)
    valid_key_val(clase.KeyVal)
    if tipo_hut is not None:
        if tipo_hut == "ingesta":
            ingesta(clase)
        elif tipo_hut == "hammurabi":
            hammurabi(clase)
        elif tipo_hut == "Control M":
            malla(clase)

