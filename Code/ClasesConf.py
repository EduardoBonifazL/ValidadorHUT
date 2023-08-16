from pyhocon import ConfigFactory
from pyhocon.exceptions import ConfigMissingException
import re
import os


class Config:
    def __init__(self, key, value):
        self.key = key.split('/')
        self.uuaa = self.key[-4]
        self.tabla = self.key[-3]
        self.capa = self.key[-2]
        self.name = self.key[-1]
        self.value = value
        self.set_variables()
        self.conf = ConfigFactory.parse_string(value)

    def set_variables(self):
        list_var = list(set(re.findall(r"(?<=\$\{)[?A-Z0-9_]+(?=})", self.value)))
        for var in list_var:
            if '?' in var:
                var = var.replace('?', '')
                os.environ[var] = '${?'+var+'}'
            else:
                os.environ[var] = '${'+var+'}'

    def get_conf_value(self, ruta: str):
        try:
            value = self.conf.get_string(ruta)
        except ConfigMissingException:
            return
        return value


class KirbyConf(Config):
    def __init__(self, key, value):
        super().__init__(key, value)
        self.InputType = self.get_conf_value("kirby.input.type")
        self.InputSchemaPath = self.get_conf_value("kirby.input.schema.path")
        self.InputPaths = self.get_conf_value("kirby.input.paths")
        self.InputApplyConversions = self.get_conf_value("kirby.input.applyConversions")
        self.InputOverrideSchema = self.get_conf_value("kirby.input.options.overrideSchema")
        self.InputIncludeMetadataAndDeleted = self.get_conf_value("kirby.input.options.includeMetadataAndDeleted")
        self.OutputType = self.get_conf_value("kirby.output.type")
        self.OutputMode = self.get_conf_value("kirby.output.mode")
        self.OutputForce = self.get_conf_value("kirby.output.force")
        self.OutputPath = self.get_conf_value("kirby.output.path")
        self.OutputSchemaPath = self.get_conf_value("kirby.output.schema.path")
        self.OutputDropLeftoverFields = self.get_conf_value("kirby.output.dropLeftoverFields")
        self.OutputPartitionOverwriteMode = self.get_conf_value("kirby.output.options.partitionOverwriteMode")
        self.OutputPartition = self.get_conf_value("kirby.output.partition")
        print(f'\nEvaluando {self.capa}/{self.name}:')

    def valid_override_schema(self):
        if self.InputType == 'parquet':
            if self.InputOverrideSchema == 'true':
                comentario = 'Se encontró input.options.overrideSchema = "true"'
                estado = 'OK'
            else:
                comentario = 'No se encontró input.options.overrideSchema = "true"'
                estado = 'FAILURE'
            print(f'* {comentario}: {estado}')
        else:
            if self.InputOverrideSchema == 'true':
                comentario = 'overrideSchema = "true" solo aplica a "parquet"'
                estado = 'FAILURE'
                print(f'* {comentario}: {estado}')

    def valid_input_schema_path(self):
        variables = '${ARTIFACTORY_UNIQUE_CACHE}"/artifactory/"${SCHEMAS_REPOSITORY}'
        if '${ARTIFACTORY_UNIQUE_CACHE}/artifactory/${SCHEMAS_REPOSITORY}' in self.InputSchemaPath:
            comentario = f'Se encontró {variables} en input.schema.path'
            estado = 'OK'
        else:
            comentario = f'No se encontró {variables} en input.schema.path'
            estado = 'FAILURE'
        print(f'* {comentario}: {estado}')
        if '/latest/' in self.InputSchemaPath:
            comentario = 'Se encontró latest en input.schema.path'
            estado = 'OK'
        else:
            comentario = 'No se encontró latest en input.schema.path'
            estado = 'WARNING'
        print(f'* {comentario}: {estado}')

    def valid_input_path(self):
        print(f'* {self.InputPaths}')

    def valid_output_schema_path(self):
        variables = '${ARTIFACTORY_UNIQUE_CACHE}"/artifactory/"${SCHEMAS_REPOSITORY}'
        if '${ARTIFACTORY_UNIQUE_CACHE}/artifactory/${SCHEMAS_REPOSITORY}' in self.OutputSchemaPath:
            comentario = f'Se encontró {variables} en output.schema.path'
            estado = 'OK'
        else:
            comentario = f'No se encontró {variables} en output.schema.path'
            estado = 'FAILURE'
        print(f'* {comentario}: {estado}')
        if '/latest/' in self.OutputSchemaPath:
            comentario = 'Se encontró latest en output.schema.path'
            estado = 'OK'
        else:
            comentario = 'No se encontró latest en output.schema.path'
            estado = 'WARNING'
        print(f'* {comentario}: {estado}')

    def valid_include_metadata_and_deleted(self):
        if self.InputType == 'parquet' and self.capa in ['raw', 'master']:
            if self.InputIncludeMetadataAndDeleted == 'true':
                comentario = 'Se encontró input.options.includeMetadataAndDeleted = "true"'
                estado = 'OK'
            else:
                comentario = 'No se encontró input.options.includeMetadataAndDeleted = "true"'
                estado = 'FAILURE'
            print(f'* {comentario}: {estado}')
        else:
            if self.InputIncludeMetadataAndDeleted is not None:
                comentario = 'includeMetadataAndDeleted solo aplica a "parquet" y en capa "raw" o "master"'
                estado = 'FAILURE'
                print(f'* {comentario}: {estado}')

    def valid_drop_left_over_fields(self):
        if self.OutputType in ['avro', 'parquet'] and self.capa in ['raw', 'master']:
            if self.OutputDropLeftoverFields == 'true':
                comentario = 'Se encontró output.dropLeftoverFields = "true"'
                estado = 'OK'
            else:
                comentario = 'No se encontró output.dropLeftoverFields = "true"'
                estado = 'FAILURE'
            print(f'* {comentario}: {estado}')
        else:
            if self.OutputDropLeftoverFields is not None:
                comentario = 'dropLeftoverFields solo aplica a "avro" o "parquet" y en capa "raw" o "master"'
                estado = 'FAILURE'
                print(f'* {comentario}: {estado}')

    def valid_apply_conversions(self):
        if self.InputType == 'avro':
            if self.InputApplyConversions == "false":
                comentario = 'Se encontró input.applyConversions = "false"'
                estado = 'OK'
            else:
                comentario = 'No se encontró input.applyConversions = "false"'
                estado = 'FAILURE'
            print(f'* {comentario}: {estado}')
        else:
            if self.InputApplyConversions == 'true':
                comentario = 'applyConversions = "false" solo aplica a "avro"'
                estado = 'FAILURE'
                print(f'* {comentario}: {estado}')

    def valid_force(self):
        if self.OutputForce == "true":
            comentario = 'Se encontró output.force = "true"'
            estado = 'OK'
        else:
            comentario = 'No se encontró output.force = "true"'
            estado = 'FAILURE'
        print(f'* {comentario}: {estado}')

    def valid_mode(self):
        if self.OutputMode == "overwrite":
            comentario = 'Se encontró output.mode = "overwrite"'
            estado = 'OK'
        else:
            comentario = 'No se encontró output.mode = "overwrite"'
            estado = 'FAILURE'
        print(f'* {comentario}: {estado}')

    def valid_partition_over_write_mode(self):
        if self.OutputPartitionOverwriteMode == "dynamic":
            comentario = 'Se encontró output.options.partitionOverwriteMode = "dynamic"'
            estado = 'OK'
        else:
            comentario = 'No se encontró output.options.partitionOverwriteMode = "dynamic"'
            estado = 'FAILURE'
        print(f'* {comentario}: {estado}')

    def valid_output_path(self):
        path = f'/data/{self.capa}/{self.uuaa}/data/{self.tabla}'
        if self.OutputPath == path:
            comentario = f'output.path = {path}'
            estado = 'OK'
        else:
            comentario = f'Se esperaba output.path = {path}'
            estado = 'FAILURE'
        print(f'* {comentario}: {estado}')

    def valid_conf(self):
        self.valid_override_schema()
        self.valid_input_schema_path()
        # self.valid_input_path()
        self.valid_output_schema_path()
        self.valid_include_metadata_and_deleted()
        self.valid_drop_left_over_fields()
        self.valid_apply_conversions()
        self.valid_force()
        self.valid_mode()
        self.valid_partition_over_write_mode()
        # self.valid_output_path()


class HammurabiConf(Config):
    def __init__(self, key, value):
        super().__init__(key, value)
