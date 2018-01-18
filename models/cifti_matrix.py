import nibabel
import numpy as np
import subprocess
import time
import pandas as pd
import os

class CiftiMatrix():
    def __init__(self, path, wb_command_path_prefix):
        # probably not necessary on normal environments but helpful for setting when running from pycharm during development
        self.wb_command_path_prefix = wb_command_path_prefix

        # cift2.load returns a Cifti2Image
        # which inherits from a DataobjImage
        # http: // nipy.org / nibabel / reference / nibabel.cifti2.html  # nibabel.cifti2.cifti2.Cifti2Image

        output_path = path + ".csv"
        start_time = time.time()

        wb_command_text = os.path.join(self.wb_command_path_prefix, "wb_command")
        print(wb_command_text)
        result = subprocess.run([wb_command_text, "-cifti-convert", "-to-text", path, output_path])

        data_file = pd.read_csv(output_path)

        os.remove(output_path)

        self.data = data_file[data_file.columns[0]]

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
