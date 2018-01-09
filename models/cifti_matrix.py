import nibabel
import numpy as np
import subprocess
import time
import pandas as pd
import os

class CiftiMatrix():
    def __init__(self, path):

        # cift2.load returns a Cifti2Image
        # which inherits from a DataobjImage
        # http: // nipy.org / nibabel / reference / nibabel.cifti2.html  # nibabel.cifti2.cifti2.Cifti2Image

        output_path = path + ".csv"
        start_time = time.time()

        result = subprocess.run(["wb_command", "-cifti-convert", "-to-text", path, output_path])

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
