from models.cifti import *
import os
import numpy as np

class CiftiSet():
    def __init__(self,path_list):
        self._path_list = path_list
        self.ciftiMatrices = {}


    def verify_paths(self):
        not_found = []
        for path in self._path_list:
            if not os.path.exists(path):
                not_found.append(path)
        return not_found

    def load_all(self):
        #todo monitor memory usage

        #todo monitor matrix shape amd make sure they are matching.

        last_shape = None

        self.ciftiMatrices = {}
        for i,path in enumerate(self._path_list):
            if os.path.exists(path):
                c = Cifti(path)
                m = c.matrix()
                if last_shape == None:
                    last_shape = m.shape
                else:
                    if m.shape != last_shape:
                        raise ValueError('Cifti Matrix Size Mismatch',"%s with a shape of %s does not match the others with a shape of %s" % (path,str(m.shape),str(last_shape)))
                    print(m.shape)
                self.ciftiMatrices[i] = c.matrix()
            else:
                raise ValueError('Cifti missing',"%s not found" % path)
        self._shape = last_shape[1]

        #todo combine into a 3d numpy matrix

    def getVectorPosition(self,i):

        #todo assumes validation has already confirmed all are the same shape
        shape = self.ciftiMatrices[0].shape

        vector = np.zeros(len(self.ciftiMatrices))

        for k,v in self.ciftiMatrices.items():
            print(type(v))

            vector[k] = v[0,i]

        return vector

    @property
    def shape(self):
        """returns the number of elements in the vector"""
        return self._shape

