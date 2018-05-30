import nibabel
import numpy as np
import subprocess
import time
import pandas as pd


class Cifti():
    def __init__(self, path, use_wbcommand=False):

        # cift2.load returns a Cifti2Image
        # which inherits from a DataobjImage
        # http: // nipy.org / nibabel / reference / nibabel.cifti2.html  # nibabel.cifti2.cifti2.Cifti2Image

        if use_wbcommand:
            self.loadViaWbCommand(path)
        else:
            self._cifti = nibabel.cifti2.cifti2.load(path)

    def loadViaWbCommand(self, path):
        # alternative :  wb_command -cifti-convert -to-text cub-sub-NDARINV02EBX0JJ_FNL_preproc_v2_Atlas_SMOOTHED_1.7.dtseries.nii_10_minutes_of_data_at_FD_0.2.dconn.nii_to_Merged_HCP_best80_dtseries.conc_AVG.dconn.dscalar.nii

        # or wb_command -nifti-information -print-matrix base_output.dscalar.nii
        i = 0
        output_path = path + ".csv"
        start_time = time.time()

        result = subprocess.run(["wb_command", "-cifti-convert", "-to-text", path, output_path])
        data = pd.read_csv(output_path)

    @property
    def matrix(self):

        return self._cifti.get_fdata()

    @property
    def vector(self):
        return self.matrix[0]

    def setVector(self, new_values):
        # check for length mismatch
        if len(new_values) == self.size:
            self._cifti.get_fdata()[0, :] = new_values
        else:
            raise ValueError(
                "Size mismatch when attempting to set Cifti Vector (new vector size: %d, existing size: %d" % (
                    len(new_values), self.size))

    @property
    def size(self):
        return len(self._cifti.get_fdata()[0, :])

    def setPosition(self, vector_position, value):
        self._cifti.get_fdata()[0, vector_position] = value

    def getPosition(self, vector_position):
        return self._cifti.get_fdata()[0, vector_position]

    def save(self, path):
        """Save the cifti to disk.
        The data in the loaded Cifti2Image appears to be read only so
        :param path:
        :return:
        """

        orig_cifti = self._cifti

        data = orig_cifti.get_fdata()

        new_cifti = nibabel.cifti2.cifti2.Cifti2Image(data,
                                                      orig_cifti.header,
                                                      orig_cifti.nifti_header,
                                                      orig_cifti.extra,
                                                      orig_cifti.file_map)

        nibabel.cifti2.cifti2.save(new_cifti, path)

        self._cifti = new_cifti

    def nullify(self):
        n = len(self.vector)
        for i in range(n):
            self.setPosition(i, np.nan)

    def randomize(self):
        """just for testing, make a random cift"""
        n = len(self.vector)
        value = 0
        for i in range(n):
            if i % 1000 == 0:
                value += 1
                self.setPosition(i, value)
