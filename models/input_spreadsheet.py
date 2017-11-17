import pandas as pd
import numpy as np


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
        self.cleaned.to_csv(path, header=False, index=False)

    def prepare_with_cifti(self):
        if True:
            print("todo")
