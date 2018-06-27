import nibabel
import numpy as np
import subprocess
import time
import pandas as pd
import os
import random

class CiftiMatrix():
    def __init__(self, path, wb_command_path_prefix):
        # probably not necessary on normal environments but helpful for setting when running from pycharm during development
        self.wb_command_path_prefix = wb_command_path_prefix

        # cift2.load returns a Cifti2Image
        # which inherits from a DataobjImage
        # http: // nipy.org / nibabel / reference / nibabel.cifti2.html  # nibabel.cifti2.cifti2.Cifti2Image
       
        #It needs to write a temporary csv file of just the numbers.
        #the source dir of the ciftis is not necessarily writeable to the 
        #user running this so it writes that temporary csv to the users home directory
        #and deletes it shortly later.  A random number is prepended to the filename
        #to avoid name collisions 
        output_filename = str(random.randint(1,100000000)) + "." + os.path.basename(path)+".csv"

        output_path = os.path.expanduser(os.path.join("~",output_filename))
        start_time = time.time()

        wb_command_text = os.path.join(self.wb_command_path_prefix, "wb_command")
        try:
            result = subprocess.run([wb_command_text, "-cifti-convert", "-to-text", path, output_path])

            # VERY important to not let pandas infer a header row here,
            # could cause on off-by-one error.
            # there is no header row in the output of the cifti-convert command!
            data_file = pd.read_csv(output_path, header=None)

            os.remove(output_path)

            self.data = data_file[data_file.columns[0]]
        except:
            raise ValueError("Error using workbench command to read cifti data at %s, perhaps you do not have write permissions in this location." % path)

    @property
    def matrix(self):
        return self.data

    @property
    def vector(self):
        return self.data

    @property
    def size(self):
        return len(self.data)

    def getPosition(self, vector_position):
        return self.data[vector_position]

    def setPosition(self, vector_position, value):
        self.data[vector_position] = value

    def nullify(self):
        n = len(self.vector)
        for i in range(n):
            self.setPosition(i, np.nan)
