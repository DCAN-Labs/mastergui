import re
import pandas as pd

# this is a scratch file used to build the function bene requires. It imports an
# mplus output and spares this poor user from having to run mastergui over and over again.




Model_Fit_Information_Label = "MODEL_FIT_INFORMATION"
Model_Results_Label = "MODEL_RESULTS"
Standarized_Model_Results_Label = "STANDARDIZED_MODEL_RESULTS"
key_delimiter = "-"
Model_Termination_Section_Label = "THE_MODEL_ESTIMATION_TERMINATED_NORMALLY"
Sample_Statistics_Label = "SAMPLE_STATISTICS"
# self.sections[Sample_Statistics_Label] = ["Happy Chaunaka"]
# grabbing mplus file
mplus = open('mplus_output.txt', 'r').readlines()
Sample_Statistics_Label = "SAMPLE_STATISTICS"


def process_sample_stats(self, title, lines):

    """
    This function accepts a list of strings that contain the entire output
    of an mplus report. It then parses those strings and extracts the
    relevant information and places it into a dictionary for output.
    The format of the input strings can be seen below.

    SAMPLE STATISTICS


        ESTIMATED SAMPLE STATISTICS


        Means
            C21           C36           C11           C4            RLNIL6
            ________      ________      ________      ________      ________
            3.202         3.127         3.249         3.466         0.775

        Means
            RMDIET        RSEX
            ________      _______
            0.595         0.548


        Covariances
            C21           C36           C11           C4            RLNIL6
             ________      ________      ________      ________      ________
C21            0.112
C36            0.057         0.063
C11            0.037         0.019         0.061
C4             0.095         0.044         0.029         0.115
RLNIL6        -0.002         0.011         0.005         0.002         0.097
RMDIET         0.052         0.013         0.039         0.036        -0.003
RSEX           0.084         0.034         0.029         0.050        -0.008

        Covariances
            RMDIET        RSEX
            ________      ________
            RMDIET         0.241
            RSEX           0.126         0.248


            Correlations
                C21           C36           C11           C4            RLNIL6
             ________      ________      ________      ________      ________
C21            1.000
C36            0.682         1.000
C11            0.451         0.307         1.000
C4             0.839         0.513         0.349         1.000
RLNIL6        -0.019         0.144         0.063         0.019         1.000
RMDIET         0.318         0.109         0.323         0.215        -0.022
RSEX           0.506         0.271         0.236         0.294        -0.055


            Correlations
                RMDIET        RSEX
            ________      ________
RMDIET         1.000
RSEX           0.517         1.000


    MAXIMUM LOG-LIKELIHOOD VALUE FOR THE UNRESTRICTED (H1) MODEL IS -55.905
"""
    # checking to see when this section gets created
    # you need to check multiple times on multiple lines for these
    # headings/output
    things_to_check = ['Means', 'Covariances', 'Correlations']

    # beginning to write parser for sample stats
    first_char_finder = re.compile('([A-Z])')
    column_names = []
    section_data = {}
    ws = re.compile('\s+')
    for line in lines:
        m = re.search(first_char_finder,line)
        if m:
            idx = m.start()
            if idx == 20:
                pass


def process_results_table(self, title, lines):
    """
        Parse the MODEL RESULTS section

        Sample Mplus output contents:

        MODEL RESULTS

                                                            Two-Tailed
                            Estimate       S.E.  Est./S.E.    P-Value

         Means
            NUC_ACC_VI         0.067      0.025      2.709      0.007
            PC6                0.016      0.004      4.287      0.000
            PC1               -0.026      0.032     -0.820      0.412
            VOX               -0.117      0.123     -0.951      0.342
            PGS                0.478      0.087      5.494      0.000

         Variances
            NUC_ACC_VI         0.002      0.001      2.449      0.014
            PC6                0.000      0.000      2.449      0.014
            PC1                0.003      0.001      2.449      0.014
            VOX                0.046      0.019      2.449      0.014
            PGS                0.023      0.009      2.449      0.014

    """
    # print("Begin parse table "  + title)
    first_char_finder = re.compile('([A-Z])')
    column_names = []
    section_data = {}
    ws = re.compile('\s+')
    for line in lines:
        m = re.search(first_char_finder, line)
        if m:
            idx = m.start()
            # print("Start index %d" % idx)
            # print(line)
            if idx == 20:
                column_names = re.split(ws, line.strip())
            elif idx == 1:
                stat_type = line.strip()
            elif idx == 4:
                # print("it was idx4")
                # print(line)
                parts = re.split(ws, line.strip())
                # if len(parts) == 5:
                stat_name = parts[0]
                keyprefix = key_delimiter.join([title, stat_type, stat_name])
                for i in range(1, len(parts)):
                    keyname = keyprefix + key_delimiter + column_names[i - 1]
                    try:
                        value = float(parts[i])
                        self.setDataValue(keyname, value)
                        section_data[keyname] = value
                    except:

                        if self.limited_parse:
                            if keyname in self.limit_to_keys:
                                self.logNumberParsingError(keyname)
                                # otherwise we can just ignore it
                        else:
                            self.logNumberParsingError(keyname)

    self.sections[title] = section_data



df = pd.read_fwf('mplus_output.txt')
print(df)
table = pd.read_table('mplus_output.txt', sep='\s+')
print(table)