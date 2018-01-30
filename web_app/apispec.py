"""
自动model转restful_api swagger生成器
"""
import yaml

class ApiSpec():
    """
    生成器
    """
    def __init__(self, title, description, version):
        """
        仅支持openapi:3.0.0
        """
        self._schemas = {}
        self._paths = {}
        self._tags = []
        self._parameters = {}
        self._spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "description": description,
                "version": version
            },
            "paths": self._paths,
            "tags": self._tags,
            "components": {
                "schemas": self._schemas,
                "parameters": self._parameters
            }
        }

    def add_schema(self, name, schema):
        """
        添加schema
        """
        self._schemas[name] = schema

    def add_path(self, name, path):
        """
        添加path
        """
        self._paths[name] = path

    def add_parameters(self, name, parameter):
        """
        添加全局参数
        """
        self._parameters[name] = parameter

    def add_tag(self, name, doc):
        """
        添加标签
        """
        self._tags.append({
            "name": name,
            "description": doc
        })

    def to_dict(self):
        """
        提取字典
        """
        return self._spec

    def to_yaml(self):
        """
        装换为yaml
        """
        return yaml.dump(self.to_dict())
