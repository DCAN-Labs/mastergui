from models.cifti import *
import os
import numpy as np
import threading
import time


class CiftiSet():
    def __init__(self, path_list):
        self._path_list = path_list
        self.ciftis = {}

    def verify_paths(self):
        not_found = []
        for path in self._path_list:
            if not os.path.exists(path):
                not_found.append(path)
        return not_found

    def setupMatrix(self):
        #we need all ciftis to be the same size in a given set.
        #so somewhat arbitrarily we will assume that the first one in the list of
        #cifti paths has the correct size and compare all subsequent ones to taht
        first_path = self._path_list[0]
        c = Cifti(first_path)
        m = c.matrix
        allCiftiMatrix = np.zeros((len(self._path_list), m.shape[1]))
        allCiftiMatrix[:] = np.nan
        self._voxel_count = m.shape[1]
        self.cifti_shape= m.shape

        self.matrix = allCiftiMatrix



    def load_all(self):
        # todo monitor memory usage


        self.setupMatrix()

        last_shape = None

        #todo this would benefit from multiple threads as there is a lot of disk i/o time

        num_threads = 2

        threads = []

        indexed_paths = [(i,path) for i, path in enumerate(self._path_list)]

        sets_of_paths = np.array_split(indexed_paths, num_threads)


        begin_time = time.time()

        for list_of_paths in sets_of_paths:
            t = threading.Thread(target=self.readListOfCiftis,
                                 args=[list_of_paths])
            t.start()

            threads.append(t)

        for t in threads:
            t.join()
        end_time = time.time()

        print("Elapsed time for the loading of ciftiset %s" % (
            end_time - begin_time))

    def readListOfCiftis(self,indexed_path_list):

        #each entry in the indexed_path_list is a tuple (final_array_row_index, path_to_cifti)

        for t in indexed_path_list:

            row_index = int(t[0])
            path = t[1]

            if os.path.exists(path):

                start_time = time.time()

                c = Cifti(path)
                end_time = time.time()
                print("time to read cifti : %s sec " % (end_time - start_time))
                m = c.matrix

                if m.shape != self.cifti_shape:
                    raise ValueError('Cifti Matrix Size Mismatch',
                                     "%s with a shape of %s does not match the others with a shape of %s" % (
                                         path, str(m.shape), str(self.cifti_shape)))

                start_time = time.time()
                voxels_from_cifti = c.matrix[0, :]

                with threading.Lock():
                    self.matrix[row_index, :] = voxels_from_cifti
                end_time = time.time()
                print("time to add cifti vector to matrix : %s sec " % (end_time - start_time))
            else:
                raise ValueError('Cifti missing', "%s not found" % path)


    def getVectorPosition(self, i):

        return self.matrix[:, i]

    @property
    def voxel_count(self):
        """returns the number of elements in the vector"""
        return self._voxel_count
