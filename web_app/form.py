import re
import os
import json

FROM_TYPE_TO_OPENAPI = {
    "text": "string",
    "url": "string",
    "tel": "string",
    "password": "string",
    "email": "string",
    "date": "string",
    "color": "string",
    "number": "number",
    "range": "number",
    "checkbox": "boolean"
}

class Form:
    def __init__(self, form_dir):
        self._form_dir = form_dir
        self._forms = {}

    def load(self, name):
        if name not in self._forms:
            with open(os.path.join(self._form_dir, name + ".json"), encoding="utf8") as fd_json:
                form = json.load(fd_json)
            for _, val in form.items():
                if "pattern" in val:
                    val["pattern"] = re.compile(val["pattern"])
            self._forms[name] = form
            return form
        return self._forms[name]
    
    def generate_schema(self, name):
        """
        使用表单约束生成 openapi doc schema
        """
        form = self.load(name)
        schema = {
            "properties": {},
            "required": []
        }
        for key, val in form.items():
            propertie = {
                "type": "string" if val.get("type") not in FROM_TYPE_TO_OPENAPI else FROM_TYPE_TO_OPENAPI[val["type"]],
                "description": val.get("placeholder")
            }
            if "min" in val:
                propertie["minimum"] = val["min"]
            if "max" in val:
                propertie["maximum"] = val["max"]
            if "minlength" in val:
                propertie["minLength"] = val["minlength"]
            if "maxlength" in val:
                propertie["maxLength"] = val["maxlength"]
            if "required" in val:
                schema["required"].append(key)
            schema["properties"][key] = propertie
        return schema

    def verify(self, name, form_data):
        form = self.load(name)
        message = None
        for key, val in form.items():
            if not val or ("sort" in val and (val["sort"] == 0 or val["sort"] == 2)):
                continue
            if (key not in form_data or form_data[key] == "") and val["required"]:
                message = "%s: 必填!" % key
                break
            value = form_data[key]
            # name = val["placeholder"]
            name = key
            if "min" in val:
                min_ = val['min']
                if value < min_:
                    message = "%s: 不能小于%d!" % (name, min_)
                    break
            elif "max" in val:
                max_ = val['max']
                if value > max_:
                    message = "%s: 不能大于%d!" % (name, max_)
                    break
            elif "minlength" in val:
                minlength = val["minlength"]
                if len(value) < minlength:
                    message = "%s: 长度不能小于%d!" % (name, minlength)
                    break
            elif "maxlength" in val:
                maxlength = val["maxlength"]
                if len(value) > maxlength:
                    message = "%s: 长度不能大于%d!" % (name, maxlength)
                    break
            elif "pattern" in val:
                pattern = val["pattern"]
                if not pattern.match(value):
                    message = "%s: 无法匹配正则!" % name
                    break
            elif "equal" in val:
                equal = val["equal"]
                if form_data[equal] != value:
                    message = "%s: 与 `%s` 不相同!" % (name, equal)
                    break
        return {"status": 401, "message": message} if message else message 
        

