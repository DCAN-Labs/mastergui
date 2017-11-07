import yaml


class Config():
    def __init__(self, path=""):
        self._path = path
        if len(path) > 0:
            self.load()

    def load(self):
        with open(self._path, 'r') as f:
            self._data = yaml.load(f)
        print(self._data)
