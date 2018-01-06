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

class FconnanovaAnalysis(Analysis):
    def __init__(self, config, filename = "", saved_data = None):
        super(FconnanovaAnalysis, self).__init__(config, "fconnanova", filename)
        self.required_config_keys = ['output_dir']
