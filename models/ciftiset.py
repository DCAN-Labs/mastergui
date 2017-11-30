from models.cifti import *
import os
import numpy as np


class CiftiSet():
    def __init__(self, path_list):
        self._path_list = path_list
        self.ciftiMatrices = {}  # todo kill off ciftiMatrices
        self.ciftis = {}

    def verify_paths(self):
        not_found = []
        for path in self._path_list:
            if not os.path.exists(path):
                not_found.append(path)
        return not_found

    def load_all(self):
        # todo monitor memory usage

        # todo monitor matrix shape amd make sure they are matching.

        last_shape = None

        # self.ciftiMatrices = {}
        self.matrix = None

        for i, path in enumerate(self._path_list):
            if os.path.exists(path):
                c = Cifti(path)
                m = c.matrix
                if last_shape == None:
                    last_shape = m.shape
                else:
                    if m.shape != last_shape:
                        raise ValueError('Cifti Matrix Size Mismatch',
                                         "%s with a shape of %s does not match the others with a shape of %s" % (
                                             path, str(m.shape), str(last_shape)))

                if i == 0:
                    allCiftiMatrix = np.zeros((len(self._path_list), m.shape[1]))
                    allCiftiMatrix[:] = np.nan
                allCiftiMatrix[i, :] = c.matrix[0, :]
                # self.ciftiMatrices[i] = c.matrix
                # self.ciftis[i] = c
            else:
                raise ValueError('Cifti missing', "%s not found" % path)
        self._shape = last_shape[1]
        self.matrix = allCiftiMatrix

    def getVectorPosition(self, i):

        return self.matrix[:, i]

    @property
    def shape(self):
        """returns the number of elements in the vector"""
        return self._shape
