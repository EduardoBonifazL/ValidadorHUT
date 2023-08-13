from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from pyhocon import ConfigFactory
# from pyhocon.exceptions import ConfigMissingException
from Code.Constantes import \
    UserViewXpath, UserStatusXpath, FolderClosedXpath, FileXpath, FileSegmentXpath, FileSourceXpath, FileBodyXpath,\
    TeamBacklogHistoryXpath
import pandas as pd
import os
import re


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
    except TimeoutException:
        return


def get_list(driver, xpath: str, t=1, text=True):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        xpath_list = driver.find_elements(By.XPATH, xpath)
        if text:
            return list(map(lambda x: x.text, xpath_list))
        else:
            return xpath_list
    except TimeoutException:
        return


def get_attribute(driver, xpath: str, attribute: str, t=1):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        return driver.find_element(By.XPATH, xpath).get_attribute(attribute)
    except TimeoutException:
        return


def get_value_link(driver, xpath: str, t=1):
    try:
        WebDriverWait(driver, t).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        return [get_value(driver, xpath, 1), get_attribute(driver, xpath, "href")]
    except TimeoutException:
        return


def get_po(team_backlog):
    lideres_df = pd.read_excel(
        './Resource/[DQA] Lideres Datio - Acuerdos EdP.xlsx',
        sheet_name=os.environ["Q"],
        dtype='object'
    ).dropna(subset='Dom')
    for index, data in lideres_df.iterrows():
        if type(data['Tablero']) == str and team_backlog in data['Tablero']:
            if type(data['PO']) == str:
                po_list = [transform_assigned(x) for x in data['PO'].replace('@bbva.com', '').split('\n')]
                if type(data['PO Temporal']) == str:
                    po_list.extend(
                        [transform_assigned(x) for x in data['PO Temporal'].replace('@bbva.com', '').split('\n')])
                return list(set(po_list))
            break
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
                 transform_assigned(row.find_element(By.XPATH, 'td[@class="assignee"]').text)]
            )
        return sub_task
    except TimeoutException:
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
    except TimeoutException:
        return


def expand_history(driver, t=1):
    expanded = get_attribute(driver, '//*[@id="activitymodule_heading"]/button', "aria-expanded", t)
    while expanded != "true":
        driver.find_element(By.XPATH, '//*[@id="activitymodule_heading"]/button').click()
        expanded = get_attribute(driver, '//*[@id="activitymodule_heading"]/button', "aria-expanded", 2)
    active_tab = get_value(driver, '//*[@class="menu-item  active-tab active "]')
    while active_tab != "History":
        driver.find_element(By.XPATH, '//*[@data-id="changehistory-tabpanel"]').click()
        active_tab = get_value(driver, '//*[@class="menu-item  active-tab active "]', 2)
    return get_list(driver, TeamBacklogHistoryXpath, 2)


def get_first_team(team_list):
    return re.findall(r"(?<=>)[\w\s.&-]+(?=</span>)", team_list[0])[0]


def get_user_approved(driver, t=1):
    usuarios = get_list(driver, UserViewXpath, t)
    estados = get_list(driver, UserStatusXpath)
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
    folder_closed = get_list(driver, FolderClosedXpath, t, False)
    while folder_closed is not None:
        for folder in folder_closed:
            folder.click()
        folder_closed = get_list(driver, FolderClosedXpath, text=False)
    file_list = get_list(driver, FileXpath, text=False)
    file_link = []
    for file in file_list:
        name = file.text
        for i in ['.conf', '.json', '.schema', '.feature', '.scala']:
            if i in name:
                file.click()
                file_segment = get_value(driver, FileSegmentXpath)
                while name != file_segment:
                    file_segment = get_value(driver, FileSegmentXpath)
                file_link.append(get_attribute(driver, FileSourceXpath, 'href').replace('/browse/', '/raw/'))
    for link in file_link:
        driver.get(link)
        path = link.split('?at=')[0]
        path_file[path] = get_value(driver, FileBodyXpath, 4)
    return path_file


def transform_assigned(assigned):
    assignee_text = assigned.split('.')
    assignee = assignee_text[:-1] if assignee_text[-1] == 'contractor' else assignee_text
    return ' '.join(assignee).upper()


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


def valid_acceptance_criteria(accept_crit, accept_crit_value: str):
    estado = "FAILURE"
    if accept_crit is not None:
        if accept_crit == accept_crit_value:
            comentario = f'Criterio de Aceptación "{accept_crit}"'
            estado = "OK"
        else:
            comentario = f'Se encontró Criterio de Aceptación "{accept_crit}", se esperaba "{accept_crit_value}"'
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


def valid_team_qa(team_backlog):
    estado = "FAILURE"
    if team_backlog == 'Peru - PE Data Quality':
        comentario = f'HUT asignada a tablero "Peru - PE Data Quality"'
        estado = "OK"
    else:
        comentario = f'Aun no ha sido asignada a tablero "Peru - PE Data Quality"'
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


def valid_feature(feature_program):
    estado = "FAILURE"
    comentario = "No se encontró Feature asignado"
    if feature_program is not None:
        if feature_program[1] == "IN PROGRESS":
            comentario = f'Feature en estado "IN PROGRESS"'
            estado = "OK"
        else:
            estado = "FAILURE"
            comentario = f'Se encontró Feature en estado "{feature_program[1]}", se esperaba "IN PROGRESS"'
        print(f'* {comentario}: {estado}')
        q = os.environ["Q"].split('-')[0]
        estado = "WARNING"
        comentario = f'No se encontró vigencia del Feature en "{q}"'
        for program in feature_program[0]:
            if q in program:
                estado = "OK"
                comentario = f'Feature vigente del "{q}"'
                break
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


def contains_elements(sublista, lista):
    for elemento in sublista:
        if elemento not in lista:
            return False
    return True


def contains_name(sublista, lista):
    return contains_elements(sublista, lista) or contains_elements(lista, sublista)


def valid_sub_tasks(sub_tasks: list, tarea, status, asignado_text, asignado_list: list):
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
                if asignado_list is not None:
                    find = False
                    for asignado in asignado_list:
                        if contains_name(asignado.lower().split(' '), sub_task[3].lower().split(' ')):
                            comentario = f'Subtarea {tarea} {asignado_text}'
                            estado = "OK"
                            find = True
                            break
                    if not find:
                        comentario = f'Subtarea {tarea} asignado {sub_task[3]} se esperaba {asignado_list}'
                        estado = "FAILURE"
                else:
                    comentario = 'No se encontró PO para el Team Backlog de creación revisar "Lideres Datio"'
                    estado = "WARNING"
                print(f'* {comentario}: {estado}')
                break
    else:
        print(f'* Se esperaba documento {tarea}: {estado}')


def valid_team_backlog_created(team_backlog_created, team_value):
    estado = "FAILURE"
    if team_backlog_created != team_value:
        estado = "OK"
        comentario = f'La HUT fue creada en tablero "{team_backlog_created}"'
    else:
        comentario = f'La HUT a sido creada o clonada desde tablero de QA'
    print(f'* {comentario}: {estado}')


def valid_pull_request(pull_request: list):
    estado = "FAILURE"
    comentario = 'No se encontró Pull Request asociada'
    if pull_request is not None:
        if pull_request[0] == "1 pull request":
            estado = "OK"
            comentario = 'HUT asociada a una sola Pull Request'
    print(f'* {comentario}: {estado}')


def valid_dependency(child_item: list, feature_link: list, status):
    estado = "FAILURE"
    comentario = "No se encontró Dependencia asignada"
    if child_item is not None:
        for child in child_item:
            if child[3] == status:
                estado = "OK"
                comentario = f'HUT asignada a Dependencia {child[0]} y estado {child[3]}'
            else:
                estado = "FAILURE"
                comentario = f'HUT asignada a Dependencia {child[0]} y estado {child[3]} se esperaba {status}'
            print(f'* {comentario}: {estado}')
            if feature_link is not None:
                if child[4] == feature_link:
                    estado = "OK"
                    comentario = f'Feature Link de HUT y Dependencia {child[0]} son iguales'
                else:
                    estado = "FAILURE"
                    comentario = f'Feature Link de HUT y Dependencia {child[0]} no son iguales'
                print(f'* {comentario}: {estado}')
    else:
        print(f'* {comentario}: {estado}')


def valid_build_passed(pull_request, latest_build_status):
    if pull_request is not None:
        estado = "FAILURE"
        comentario = f'No se encontró Build'
        if latest_build_status is not None:
            if latest_build_status == 'Passed':
                estado = "OK"
                comentario = f'Se encontró el ultimo build en estado {latest_build_status}'
            else:
                estado = "FAILURE"
                comentario = f'Se encontró el ultimo build en estado {latest_build_status}, se esperaba Passed'

        print(f'* {comentario}: {estado}')


def set_variables(file):
    list_var = list(set(re.findall(r"(?<=\$\{)[?A-Z0-9_]+(?=})", file)))
    for var in list_var:
        if '?' in var:
            var = var.replace('?', '')
            os.environ[var] = '"${?'+var+'}"'
        else:
            os.environ[var] = '"${'+var+'}"'


def valid_conf_hammurabi(files):
    if files is not None:
        for key, value in files.items():
            if ".conf" in key:
                set_variables(value)
                conf = ConfigFactory.parse_string(value)
                # value = conf.get_string("data")
                print(conf)


def ingesta(clase):
    valid_type(clase.Type, "Story")
    valid_team_qa(clase.TeamBacklog)
    valid_label(clase.Labels, ['ReleasePRDatio'])
    valid_feature(clase.FeatureProgram)
    valid_acceptance_criteria(clase.AcceptanceCriteria, "Desarrollo según los Lineamientos del Equipo de DQA.")
    valid_team_backlog_created(clase.TeamBacklogCreated, 'Peru - PE Data Quality')
    valid_status(clase.Status, "READY")
    valid_item_type(clase.ItemType, "Technical")
    valid_tech_stack(clase.TechStack, "Data - Dataproc")
    valid_sub_tasks(clase.SubTask, "[C204][PO]", "ACCEPTED", "asignado a PO", clase.PO)
    valid_sub_tasks(clase.SubTask, "[C204][QA]", "READY", "sin asignar", ["Unassigned"])
    valid_pull_request(clase.PullRequest)
    valid_dependency(clase.ChildItem, clase.FeatureLink, "IN PROGRESS")
    valid_build_passed(clase.PullRequest, clase.LatestBuildStatus)


def hammurabi(clase):
    valid_type(clase.Type, "Story")
    valid_team_qa(clase.TeamBacklog)
    valid_label(clase.Labels, ['ReleasePRDatio'])
    valid_feature(clase.FeatureProgram)
    valid_acceptance_criteria(clase.AcceptanceCriteria, "Desarrollo según los Lineamientos del Equipo de DQA.")
    valid_team_backlog_created(clase.TeamBacklogCreated, 'Peru - PE Data Quality')
    valid_status(clase.Status, "READY")
    valid_item_type(clase.ItemType, "Technical")
    valid_tech_stack(clase.TechStack, "Data - Dataproc")
    valid_sub_tasks(clase.SubTask, "[C204][PO]", "ACCEPTED", "asignado a PO", clase.PO)
    valid_sub_tasks(clase.SubTask, "[C204][QA]", "READY", "sin asignar", ["Unassigned"])
    valid_pull_request(clase.PullRequest)
    valid_dependency(clase.ChildItem, clase.FeatureLink, "IN PROGRESS")
    valid_build_passed(clase.PullRequest, clase.LatestBuildStatus)
    valid_conf_hammurabi(clase.Files)


def procesamiento(clase):
    valid_type(clase.Type, "Story")
    valid_team_qa(clase.TeamBacklog)
    valid_label(clase.Labels, ['ReleasePRDatio'])
    valid_feature(clase.FeatureProgram)
    valid_acceptance_criteria(clase.AcceptanceCriteria, "Desarrollo según los Lineamientos del Equipo de DQA.")
    valid_team_backlog_created(clase.TeamBacklogCreated, 'Peru - PE Data Quality')
    valid_status(clase.Status, "READY")
    valid_tech_stack(clase.TechStack, "Data - Dataproc")
    valid_sub_tasks(clase.SubTask, "[C204][PO]", "ACCEPTED", "asignado a PO", clase.PO)
    valid_sub_tasks(clase.SubTask, "[C204][QA]", "READY", "sin asignar", ["Unassigned"])
    valid_pull_request(clase.PullRequest)
    valid_dependency(clase.ChildItem, clase.FeatureLink, "IN PROGRESS")
    valid_build_passed(clase.PullRequest, clase.LatestBuildStatus)


def malla(clase):
    valid_type(clase.Type, "Dependency")
    valid_label(clase.Labels, ['release', 'ReleaseMallasDatio'])
    valid_status(clase.Status, "READY")
    valid_item_type(clase.ItemType, "Technical")
    valid_tech_stack(clase.TechStack, "Data - Dataproc")
    valid_sub_tasks(clase.SubTask, "[C204][PO]", "ACCEPTED", "asignado a PO", clase.PO)
    valid_sub_tasks(clase.SubTask, "[P110][AT]", "ACCEPTED", "asignado a SM", [""])  # Falta implementar verificación SM
    valid_sub_tasks(clase.SubTask, "[C204][QA]", "READY", "sin asignar", ["Unassigned"])
    valid_pull_request(clase.PullRequest)
    valid_dependency(clase.ChildItem, clase.FeatureLink, "IN PROGRESS")


def validador(clase):
    tipo_hut = valid_find_hut(clase.Summary)
    valid_key_val(clase.KeyVal)
    if tipo_hut is not None:
        if tipo_hut == "ingesta":
            ingesta(clase)
        elif tipo_hut == "hammurabi":
            hammurabi(clase)
        elif tipo_hut == "procesamiento":
            procesamiento(clase)
        elif tipo_hut == "Control M":
            malla(clase)
