import re


class MplusModel():
    def __init__(self, path=""):
        if len(path) > 0:
            self.load(path)

    def load(self, path):
        with open(path, 'r') as f:
            self._raw = f.read()
        self.parseMplus(self._raw)

    def parseMplus(self, raw):

        p = re.compile('^[^\:\n]+\:', flags=re.MULTILINE)

        key_positions = [(m.start(0), m.end(0)) for m in re.finditer(p, raw)]

        mplus_data = {}
        key_order = []
        for i in range(len(key_positions)):
            k = key_positions[i]
            key = raw[k[0]:k[1]]
            if i < len(key_positions) - 1:
                value = raw[k[1]:key_positions[i + 1][0]]
            else:
                value = raw[k[1]:]
            mplus_data[key] = value
            key_order.append(key)
        self.key_order = key_order
        self.mplus_data = mplus_data

    def set_column_names(self, names):
        print(self.key_order)
        self.mplus_data["VARIABLE:"] = ("Names are " + "\n\t".join(names) +
                                        "\nUSEVARAIABLES = #todo;\n!auxillary = #todo, \nMISSING=.;\ncluster= #todo")

    def to_string(self):
        output_str = ""
        for key in self.key_order:
            output_str += "\n" + key + "\n"
            output_str += self.mplus_data[key]

        return output_str
