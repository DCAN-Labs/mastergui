import json

class Config():
    def __init__(self, path=""):
        self._path = path
        if len(path) > 0:
            self.load()

    def load(self):

        with open(self._path, 'r') as f:
            self._data = json.load(f, strict=False)

    def getOptional(self,key, default = ""):
        if key in self._data:
            return self._data[key]
        else:
            return default