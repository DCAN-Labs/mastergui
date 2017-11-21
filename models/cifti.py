import nibabel


class Cifti():
    def __init__(self, path):

        # cift2.load returns a Cifti2Image
        # which inherits from a DataobjImage
        # http: // nipy.org / nibabel / reference / nibabel.cifti2.html  # nibabel.cifti2.cifti2.Cifti2Image
        self._cifti = nibabel.cifti2.cifti2.load(path)

    @property
    def matrix(self):

        return self._cifti.get_fdata()

    @property
    def vector(self):
        return self.matrix[0]

    def setPosition(self, vector_position, value):
        self._cifti.get_fdata()[0, vector_position] = value
        print("set to " + str(value))
        print("get value is " + str(self.getPosition(vector_position)))
        # self.vector[vector_position] = value

    def getPosition(self, vector_position):
        return self.vector[vector_position]

    def save(self, path):
        self._cifti = nibabel.cifti2.cifti2.save(self._cifti, path)

    def randomize(self):
        """just for testing, make a random cift"""
        n = len(self.vector)
        value = 0
        for i in range(n):
            if i % 1000 == 0:
                value += 1
            self.setPosition(i, value)
