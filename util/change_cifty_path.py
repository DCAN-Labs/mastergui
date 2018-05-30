import pandas as pd
import os

path = '../demo/roberttest1.csv'

f = pd.read_csv(path)
new_file_prefix = '/mnt/max/home/balld/testdata/'
colindex = -1
for row in range(f.shape[0]):
    orig = f.iloc[row, colindex]
    base = os.path.basename(orig)
    new_path = os.path.join(new_file_prefix, base)
    print(new_path)
    f.iloc[row, colindex] = new_path

f.to_csv(path + ".fixed", index=False)

f.iloc[:5, :].to_csv(path + ".5rows.fixed", index=False)
