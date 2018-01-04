import pandas as pd
import numpy as np
from models import cifti
from models import ciftiset
import os
import csv
import logging
import threading
import time


class InputSpreadsheet():
    def __init__(self, path):
        self.path = path

        path = path.strip()
        if path[-4:].lower() == ".csv":
            self._data = pd.read_csv(path)
        else:
            if path[-4:].lower() == ".xls" or path[-5:].lower() == ".xlsx":
                self._data = pd.read_excel(path)
            else:
                raise ValueError("Only files with extensions .csv, .xls, or .xlsx are supported.")

    def data(self):
        return self._data

    def columnnames(self):
        return list(self._data)

    def cleanMissingValues(self, list_of_missingvalues, standard_missing_char=".", exclude_columns=[]):
        output = self._data.copy(deep=True)
        # todo just hardcoding a col name temporarily for testing;
        # exclude_columns = ['PATH_HCP']
        for col in exclude_columns:
            output.drop(col, axis=1, inplace=True)

        # todo possibly need column specifc missing values?
        for m in list_of_missingvalues:
            output.replace(m, standard_missing_char, inplace=True)

            # output.replace(np.NaN, "DOGFOOD", inplace = True)

            # indices_where_still_empty = np.where(pd.isnull(output))
            # print(indices_where_still_empty)
        # output.loc[indices_where_still_empty]= "SECONDPASS"
        output.fillna(standard_missing_char, inplace=True)
        # self.cleaned = output
        self._data = output
        return output

    def save_cleaned_data(self, path, list_of_missingvalues, standard_missing_char=".", exclude_columns=[]):
        cleaned = self.cleanMissingValues(list_of_missingvalues, standard_missing_char, exclude_columns)
        self.save_dataframe(cleaned, path)

    def save_dataframe(self, df, path):
        df.to_csv(path, header=False, index=False, quoting=csv.QUOTE_NONNUMERIC)

    def checkForInvalidPaths(self, paths):
        invalids = []
        for i, path in enumerate(paths):
            if not os.path.exists(path):
                print("path not found: " + path)
                invalids.append((i, path))
        return invalids

    def validatePathsToCiftis(self, path_to_voxel_mappings):
        paths = []
        for mapping in path_to_voxel_mappings:
            source_col_name = mapping[0]
            paths += list(self._data[source_col_name])

        invalid_paths = self.checkForInvalidPaths(paths)

        if len(invalid_paths) > 0:
            raise ValueError("%i paths to ciftis are not valid" % len(invalid_paths))

    def loadCiftiSetFromMapping(self, mapping_tuple):
        source_col_name = mapping_tuple[0]

        paths = list(self._data[source_col_name])

        #in testing mode we can limit how many actual ciftis are loaded for time savings

        if self.limit_by_row > 0:
            paths = paths[0:self.limit_by_row]

        ciftiSet = ciftiset.CiftiSet(paths)

        with threading.Lock():
            self.ciftiSets[source_col_name] = ciftiSet

        ciftiSet.load_all()

    def cancelAnalysis(self):
        """attempt to cancel the running analyis"""
        self.cancelling = True

        for k,v in self.ciftiSets.items():
            with threading.Lock():
                v.cancelling = True


    def prepare_with_cifti(self, path_to_voxel_mappings, output_path_prefix, testing_only_limit_to_n_voxels=0,
                           standard_missing_char=".", only_save_columns=[], limit_by_row = -1):
        """generate a separate file for each voxel in a cift
        :param path_to_voxel_mappings: an array of tuples (sourcecolumnname, columnnameforvoxel)
        :param output_path_prefix:
        :param testing_only_limit_to_n_voxels:  pass a number greater than 0 here ot have it only process that number of voxels, to facillitate testing
        :return:
        """

        self.limit_by_row = limit_by_row

        # this is a slow and memory intensive step
        self.loadAllCiftis(path_to_voxel_mappings)

        base_df = self.getBaseDataFrame(only_save_columns, path_to_voxel_mappings)

        if testing_only_limit_to_n_voxels > 0:
            upper_bound = testing_only_limit_to_n_voxels
        else:
            upper_bound = self.cifti_vector_size

        num_threads = 1

        threads = []

        sets_of_voxel_indices = np.array_split(list(range(upper_bound)), num_threads)

        begin_time = time.time()

        for list_of_voxel_indices in sets_of_voxel_indices:
            t = threading.Thread(target=self.generateVoxelizedFilesForList,
                                 args=[base_df, list_of_voxel_indices, output_path_prefix,
                                       path_to_voxel_mappings, standard_missing_char
                                       ])
            t.start()

            threads.append(t)

        for t in threads:
            t.join()
        end_time = time.time()

        print("Elapsed time for the generation of the voxelized files (excluding reading ciftis) %s" % (
        end_time - begin_time))

        # release the memory, we don't need them anymore!
        self.ciftiSets.clear()

    def generateVoxelizedFilesForList(self, base_df, list_of_voxel_indices, output_path_prefix, path_to_voxel_mappings,
                                      standard_missing_char):

        # this is called for each thread.  each thread should work with its own copy of the base data frame


        base_df = base_df.copy(deep=True)

        for voxel_idx in list_of_voxel_indices:
            for mapping in path_to_voxel_mappings:
                source_col_name = mapping[0]
                new_voxel_col_name = mapping[1]
                ciftiSet = self.ciftiSets[source_col_name]

                voxel_data = ciftiSet.getVectorPosition(voxel_idx)

                base_df[new_voxel_col_name] = voxel_data

            base_df.fillna(standard_missing_char, inplace = True)
            self.save_dataframe(base_df, output_path_prefix + "." + str(voxel_idx) + ".csv")

            if self.cancelling:
                return

    def getBaseDataFrame(self, only_save_columns, path_to_voxel_mappings):
        if len(only_save_columns) > 0:
            for mapping in path_to_voxel_mappings:
                target_new_column_name = mapping[1]
                if target_new_column_name in only_save_columns:
                    only_save_columns.remove(target_new_column_name)
        base_df = self._data.copy(deep=True)
        if len(only_save_columns) > 0:
            base_df = base_df[only_save_columns]
        for mapping in path_to_voxel_mappings:
            source_col_name = mapping[0]
            if source_col_name in base_df:
                base_df = base_df.drop(source_col_name, 1)

        if self.limit_by_row >0:
            base_df = base_df.iloc[0:self.limit_by_row,:]

        return base_df

    def loadAllCiftis(self, path_to_voxel_mappings):
        self.validatePathsToCiftis(path_to_voxel_mappings)
        self.ciftiSets = {}
        self.cifti_vector_size = None
        threads = []
        for mapping in path_to_voxel_mappings:
            # start each io intensive process of loading a ciftiset in a new thread
            t = threading.Thread(target=self.loadCiftiSetFromMapping, args=[mapping])
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        # verify that they are all the same size cifti vectors
        sizes = [v.voxel_count for k, v in self.ciftiSets.items()]

        if len(set(sizes)) > 1:
            raise ValueError(
                "The length of the Cifti vector did not match for all %d columns.  Vectors lengts where %s " % (
                len(path_to_voxel_mappings, str(sizes))))

        self.cifti_vector_size = sizes[0]
