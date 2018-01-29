class MplusOutput():
    def __init__(self,path):
        #debug with tests/sample.mplus.modelwarning.out
        self.path = path
        self.load()
        self.print_report()

    def load(self):

        with open(self.path, "r") as f:
            self.lines = f.readlines()

    def terminated_normally(self):
        idx = -1
        try:
            idx = self.lines.index("THE MODEL ESTIMATION TERMINATED NORMALLY\n")
        except Exception as e:
            print("error seeking")

        return idx>=0

    def print_report(self):
        print("Analysis of Mplus Output " + self.path)
        print("Terminated normally?")
        print(self.terminated_normally())

