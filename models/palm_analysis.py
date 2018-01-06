import datetime
import os
import subprocess
from models.cifti import *

import time
import logging
import numpy as np
import threading
import queue
#import models.analysis
from models.analysis import *

class PalmAnalysis(Analysis):
    def __init__(self, config, filename="", saved_data = None):
        super(PalmAnalysis, self).__init__(config, "palm", filename)
        self.required_config_keys = ['output_dir'] #['PalmSpecCommand', 'PalmCommand', 'PalmReader_command', 'output_dir']
