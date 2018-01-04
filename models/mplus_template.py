import json


class MplusTemplate():
    def __init__(self, path):
        with open(path, 'r') as f:
            template_info = json.load(f, strict=False)
        if 'name' in template_info:
            name = template_info['name']
        else:
            name = "Unnamed Template %s" % path
        self.name = name
        self.data = template_info

    @property
    def description(self):
        return self.return_if_exists("description")

    @property
    def instructions(self):
        return self.return_if_exists("instructions")

    @property
    def rawModel(self):
        return self.return_if_exists("rawmodel")

    def return_if_exists(self, key, elsereturn=""):
        if key in self.data:
            return self.data[key]
        else:
            return elsereturn
