import pandas as pd
import numpy as np
from models import cifti
from models import ciftiset
import os
import csv


class InputSpreadsheet():
    def __init__(self, path):
        # todo detect extension (.csv, .xls) and treat appropriately
        self._data = pd.read_excel(path)

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
        self.cleaned = output
        return output

    def save_cleaned_data(self, path, list_of_missingvalues, standard_missing_char=".", exclude_columns=[]):
        self.cleanMissingValues(list_of_missingvalues, standard_missing_char, exclude_columns)
        self.save_dataframe(self.cleaned, path)

    def save_dataframe(self, df, path):
        df.to_csv(path, header=False, index=False, quoting = csv.QUOTE_NONNUMERIC)

    def checkForInvalidPaths(self,paths):
        invalids = []
        for i,path in enumerate(paths):
            if not os.path.exists(path):
                invalids.append((i,path))
        return invalids

    def prepare_with_cifti(self, path_col_name, output_path_prefix, testing_only_limit_to_n_rows=0, standard_missing_char="."):
        """generate a separate file for each voxel in a cift
        :param path_col_name:
        :param output_path_prefix:
        :param testing_only_limit_to_n_rows:  pass a number greater than 0 here ot have it only process that number of voxels, to facillitate testing
        :return:
        """
        paths = list(self._data[path_col_name])

        if testing_only_limit_to_n_rows > 0:
            paths = paths[0:testing_only_limit_to_n_rows]

        invalid_paths = self.checkForInvalidPaths(paths)

        if len(invalid_paths)>0:
            raise ValueError("%i paths to ciftis are not valid" % len(invalid_paths))

        ciftiSet = ciftiset.CiftiSet(paths)

        ciftiSet.load_all()

        n_elements = ciftiSet.shape

        self.cifti_vector_size = n_elements

        base_df = self.cleaned

        rows = len(self.cleaned.index)
        base_df = base_df.drop(path_col_name, 1)
        for i in range(n_elements):
            voxel_data = ciftiSet.getVectorPosition(i)
            base_df['voxel'] = pd.Series(voxel_data).fillna(standard_missing_char, inplace=True)
            self.save_dataframe(base_df, output_path_prefix + "." + str(i) + ".csv")

            if testing_only_limit_to_n_rows >0 and i > testing_only_limit_to_n_rows:
                break

        self.ciftiSet = ciftiSet
