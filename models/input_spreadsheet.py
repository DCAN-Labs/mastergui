import pandas as pd


class InputSpreadsheet():
    def __init__(self, path):
        # todo detect extension (.csv, .xls) and treat appropriately
        self._data = pd.read_excel(path)

    def data(self):
        return self._data

    def columnnames(self):
        return list(self._data)

    def cleanMissingValues(self, list_of_missingvalues, standard_missing_char="."):
        output = self._data.copy(deep=True)
        # todo possibly need column specifc missing values?
        for m in list_of_missingvalues:
            output = output.replace(m, standard_missing_char)

        self.cleaned = output
        return output

    def save_cleaned_data(self, path, list_of_missingvalues, standard_missing_char="."):
        self.cleanMissingValues(list_of_missingvalues, standard_missing_char)
        self.cleaned.to_csv(path, header=False)

    def prepare_with_cifti(self):
        if True:
            print("todo")