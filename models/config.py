import json
import os

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


    def addToRecentFileList(self, path):
        recents_path = self.getOptional("recent_files_path", "mastergui_recents")

        if os.path.exists(recents_path):
            with open(recents_path, 'r') as f:
                files = f.readlines()
                files.insert(0,path)

                unique_tracker = {}
                unique_files = []
                for p in files:
                    p = p.strip()
                    if len(p)>0:
                        if not p in unique_tracker:
                            unique_files.append(p)
                            unique_tracker[p] = True
        else:
            unique_files = [path]


        with open(recents_path, 'w') as f:
            f.writelines("\n".join(unique_files))




