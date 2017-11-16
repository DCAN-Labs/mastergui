import nibabel

class Cifti():
    def __init__(self,path):
        self._cifti = nibabel.cifti2.cifti2.load(path)

    def matrix(self):
        return self._cifti.get_fdata()