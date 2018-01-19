import json
import os

class Config():
    def __init__(self, path=""):
        self.path = os.path.abspath(os.path.expanduser(path))
        if len(path) > 0:
            self.load()

    def load(self):

        with open(self.path, 'r') as f:
            self._data = json.load(f, strict=False)

        self.expand_all_known_paths()

    def getOptional(self,key, default = ""):
        if key in self._data:
            return self._data[key]
        else:
            return default

    @property
    def data(self):
        return self._data

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

    def missing_keys(self,list_of_keys):

        return [k for k in list_of_keys if not k in self.data]

    def resolve_directories(self, list_of_keys_that_should_contain_directories):
        errors = []
        for key in list_of_keys_that_should_contain_directories:
            if key in self.data:
                path = self.data[key]
                expanded = os.path.expanduser(path)
                if path!=expanded:
                    self.data[key] = expanded

                if not os.path.isdir(expanded):
                   errors.append((key + ": " + expanded,"Directory Does Not Exist"))
            else:
                errors.append((key,"Config Key Does Not Exist"))
        return errors

    def fixPath(self, values, key):
        if key in values:
            orig = values[key]
            expanded_path = os.path.abspath(os.path.expanduser(orig))
            if orig != expanded_path:
                values[key] = expanded_path


    def expand_all_known_paths(self):
        d = self.data
        analyzers = d.get("analyzers",{})
        for k,v in analyzers.items():
            self.fixPath(v,'templates')

        path_keys = ["output_dir",
                     "Base_cifti_for_output",
                     "default_maps",
                     "recent_files_path"]

        for path in path_keys:
            self.fixPath(d,path)
