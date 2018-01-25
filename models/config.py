import json
import os
import sys
import datetime

log_path_key = "log_path"


class Config():
    def __init__(self, path=""):
        if len(path) == 0:
            if hasattr(sys.modules['__main__'], "__file__"):
                rootdir = os.path.dirname(sys.modules['__main__'].__file__)
                path = os.path.join(rootdir, "config.json")

        self.path = os.path.abspath(os.path.expanduser(path))
        if len(path) > 0:
            self.load()

    def load(self):

        with open(self.path, 'r') as f:
            self._data = json.load(f, strict=False)

        self.expand_all_known_paths()

        self.setSystemDefaultsForMissing()

        self.setupLogPath()

    def __getitem__(self, key):
        """makes the config object instance indexable by config key (top level keys only)

        if not found just falls back to the dictionaries standard exception raising
        """

        return self.data[key]

    def __setitem__(self, key, value):

        self.data[key] = value

    def getOptional(self, key, default=""):
        """returns key value from config data if it exists,
        otherwise the provided default value
        """
        if key in self.data:
            return self.data[key]
        else:
            return default

    @property
    def data(self):
        return self._data

    def setSystemDefaultsForMissing(self):
        defaults = [(log_path_key, "/mnt/max/shared/projects/mastergui/logs")]
        for default in defaults:
            key = default[0]
            value = default[1]
            if not key in self.data:
                self.data[default] = value

    def setupLogPath(self):
        path = self.getOptional(log_path_key)

        # the preferred usage is the config.json for the mastergui instance has a "log_path" key that
        # specifies a directory. If so we create a subdirectory under the system standard with their
        # username and create a timestamped log file underneath.
        # if the original config had not provided a directory it is assumed they provided a specific path
        # for the log and we will simply use that without any further manipulation (no user specific subfolder,
        # no timestamp in the log filename)

        if os.path.isdir(path) or len(path) == 0:
            default_filename = "mastergui%s.log" % \
                               str(datetime.datetime.now()).replace(" ", "_").replace(":", "_").replace(
                                   ".", "_")
            # then we will append their username to it
            username = os.getlogin()

            user_dir_path = os.path.join(path, username)
            if not os.path.isdir(user_dir_path):
                os.mkdir(user_dir_path)

            path = os.path.join(user_dir_path, default_filename)

            path = os.path.abspath(path)

            self.data[log_path_key] = path

    def addToRecentFileList(self, path):
        recents_path = self.getOptional("recent_files_path", "mastergui_recents")

        if os.path.exists(recents_path):
            with open(recents_path, 'r') as f:
                files = f.readlines()
                files.insert(0, path)

                unique_tracker = {}
                unique_files = []
                for p in files:
                    p = p.strip()
                    if len(p) > 0:
                        if not p in unique_tracker:
                            unique_files.append(p)
                            unique_tracker[p] = True
        else:
            unique_files = [path]

        with open(recents_path, 'w') as f:
            f.writelines("\n".join(unique_files))

    def missing_keys(self, list_of_keys):

        return [k for k in list_of_keys if not k in self.data]

    def resolve_directories(self, list_of_keys_that_should_contain_directories):
        errors = []
        for key in list_of_keys_that_should_contain_directories:
            if key in self.data:
                path = self.data[key]
                expanded = os.path.expanduser(path)
                if path != expanded:
                    self.data[key] = expanded

                if not os.path.isdir(expanded):
                    errors.append((key + ": " + expanded, "Directory Does Not Exist"))
            else:
                errors.append((key, "Config Key Does Not Exist"))
        return errors

    def fixPath(self, values, key):
        if key in values:
            orig = values[key]
            expanded_path = os.path.abspath(os.path.expanduser(orig))
            if orig != expanded_path:
                values[key] = expanded_path

    def expand_all_known_paths(self):
        d = self.data
        analyzers = d.get("analyzers", {})
        for k, v in analyzers.items():
            self.fixPath(v, 'templates')

        path_keys = ["output_dir",
                     "Base_cifti_for_output",
                     "default_maps",
                     "recent_files_path",
                     "log_path"]

        for path in path_keys:
            self.fixPath(d, path)
