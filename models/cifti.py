import nibabel
import numpy as np

class Cifti():
    def __init__(self, path):

        # cift2.load returns a Cifti2Image
        # which inherits from a DataobjImage
        # http: // nipy.org / nibabel / reference / nibabel.cifti2.html  # nibabel.cifti2.cifti2.Cifti2Image
        self._cifti = nibabel.cifti2.cifti2.load(path)

    @property
    def matrix(self):

        return self._cifti.get_fdata()

    @property
    def vector(self):
        return self.matrix[0]

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
