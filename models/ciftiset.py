from models.cifti import *
from models.cifti_matrix import *
import os
import numpy as np
import threading
import time


class CiftiSet():
    def __init__(self, path_list, wb_command_prefix=""):
        self._path_list = path_list
        self.ciftis = {}
        self.cancelling = False
        self.wb_command_prefix = wb_command_prefix

    def verify_paths(self):
        not_found = []
        for path in self._path_list:
            if not os.path.exists(path) or path==".":
                not_found.append(path)
        return not_found

    def setupMatrix(self):
        # we need all ciftis to be the same size in a given set.
        # so somewhat arbitrarily we will assume that the first non-empty one in the list of
        # cifti paths has the correct size and compare all subsequent ones to taht

        first_path = ""

        for i in range(len(self._path_list)):
            p = self._path_list[i];
            if len(p)>0 and p!=".":
                first_path = p
                break
        if first_path == "":
            print("There are no actual paths to ciftis found in your selected column so we can not create the CiftiMatrix")

        c = CiftiMatrix(first_path, self.wb_command_prefix)
        m = c.matrix
        size = m.size
        allCiftiMatrix = np.zeros((len(self._path_list), m.size))
        allCiftiMatrix[:] = np.nan
        self._voxel_count = size

        self.cifti_size = size

        self.matrix = allCiftiMatrix

    def load_all(self):

        self.setupMatrix()

        last_shape = None

        num_threads = 2  # todo parameterize this number of threads

        threads = []

        #the list of paths is being split up for processing by multiple threads but we need to
        #know the original row indexes too so they are here turned into a tuple of (index, path)
        indexed_paths = [(i, path) for i, path in enumerate(self._path_list)]

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

    def readListOfCiftis(self, indexed_path_list):

        # each entry in the indexed_path_list is a tuple (final_array_row_index, path_to_cifti)

        for t in indexed_path_list:

            if self.cancelling:
                return

            row_index = int(t[0])
            path = t[1]

            if path==".":  #this is the case where no value was provided in the source data but by now mastergui will have replaced ACTUALLY missing data with a "."
                print("Warning:  Row %d had no cifti path provided." % row_index)
            elif os.path.exists(path):

                start_time = time.time()
                try:
                    c = CiftiMatrix(path, self.wb_command_prefix)
                except Exception as e:
                    print("error loading cifti")
                    raise ValueError("Error loading cifti at path " + path)

                end_time = time.time()
                print("time to read cifti : %s sec " % (end_time - start_time))
                m = c.matrix

                if c.size != self.cifti_size:
                    raise ValueError('Cifti Matrix Size Mismatch',
                                     "%s with a shape of %s does not match the others with a shape of %s" % (
                                         path, str(c.size), str(self.cifti_size)))

                start_time = time.time()
                voxels_from_cifti = c.data  # matrix[0, :]

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
        return self.cifti_size
