import json


class MplusTemplate():
    def __init__(self, path_or_dictionary):

        if type(path_or_dictionary) == str:
            with open(path_or_dictionary, 'r') as f:
                template_info = json.load(f, strict=False)
        elif type(path_or_dictionary) == dict:
            template_info = path_or_dictionary
        else:
            raise ValueError("invalid parameter path_or_dictionary")

        if 'name' in template_info:
            name = template_info['name']
        else:

            name = "Unnamed Template %s"
        self.name = name
        self.data = template_info

    @property
    def description(self):
        return self.return_if_exists("description")

    @property
    def instructions(self):
        return self.return_if_exists("instructions")

    @property
    def variables(self):
        return self.return_if_exists("variables", {})

    @property
    def rawModel(self):
        return self.return_if_exists("rawmodel")

    def return_if_exists(self, key, elsereturn=""):
        if key in self.data:
            return self.data[key]
        else:
            return elsereturn
