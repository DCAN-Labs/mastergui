import json
import models.mplus_analysis
import models.palm_analysis
import models.fconnanova_analysis

def load(filename, config):
    with open(filename, 'r') as f:
        load_data = json.load(f)

    module_name = load_data["module"]

    if module_name == "mplus":
        a = models.mplus_analysis.MplusAnalysis(config, filename, load_data)
    elif module_name == "palm":
        a = models.palm_analysis.PalmAnalysis(config, filename, load_data)
    elif module_name == "fconnanova":
        a = models.fconnanova_analysis.FconnanovaAnalysis(config, filename, load_data)
    else:
        raise ValueError("unknown module name: %s " % module_name)

    if "execution_history" in load_data:
        exec_hist = load_data["execution_history"]
        if len(exec_hist) == 0:  # if the subclass hadn't already processed the load history add it in its raw form
            a.execution_history = exec_hist
    return a
