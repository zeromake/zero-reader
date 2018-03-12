import re
import os
import json

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

    def verify(self, name, form_data):
        form = self.load(name)
        res = None
        for key, val in form.items():
            if (key not in form_data or form_data[key] == "") and val["required"]:
                res = {
                    "status": 401,
                    "message": "%s: 必填!" % key
                }
                break
            elif "pattern" in val:
                pattern = val["pattern"]
                if not pattern.match(form_data[key]):
                    res = {
                        "status": 401,
                        "message": "%s: 无法匹配正则!" % key
                    }
                    break
            elif "equal" in val:
                equal = val["equal"]
                if form_data[equal] != form_data[key]:
                    res = {
                        "status": 401,
                        "message": "%s: 与 `%s` 不相同!" % (key, equal)
                    }
                    break
        return res
        

