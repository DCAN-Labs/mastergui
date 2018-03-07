A user interface to simplify the process of setting up and running a variety of statistical analyses.

The initial version is focused on Mplus so far, but it intended to be a platform to facillitate a variety of platforms. You can think of it as a user-interface to make it easier to configure and run Mplus models. 

See Oscar Miranda-Dominguez, Eric Earl, or David Ball for more info. 

# System Requirements
Operating System: It runs on Mac, Windows, or Linux 
Python 3.6
Qt5

Recommended: 
[Anaconda]((https://www.qt.io/download))  The Anaconda-based install procedure will handle the Python and Qt dependencies for you.

# Installation
We recommend using the Anaconda package manager for the installation, though it is not required.

## Install using Conda 
 
1. Install Anaconda, downloads and instructions for all supported OS's are availabe [here](https://www.anaconda.com/download/#macos)
2. Clone the mastergui repo to the desired location. 
3. Application dependencies are described for anaconda in the file environments.yml.  Setup the conda environment via the command:
```
conda env create
```

4. Setup configuration (see Configuration section below)

5. Activate the conda environment, which will make all those mastergui dependencies availalbe.
```
source activate mastergui-env
```

6. Launch mastergui:

```
python main.py
```

## Shortcut for running the conda-based installation
The two parts in step 5 and 6 are consolidated into a simple shell script that you can use to launch mastergui using anaconda in the future:
```
./go_conda.sh
```

# Alternative Installation Procedures
If you don't wish to use the Anaconda package manager, here are some alternative installation tips. 

### 1. Make sure Python is installed on the system
```
python --version
```
You should have something in the 3.6 family MasterGui is currently tested on 3.6.3.
 
### 2. Install Qt5

Qt5 Instructions vary by operating system.  For Windows and Mac there are installation packages available [here](https://www.qt.io/download).
 

### 3. Install virtualenv
Virtualenv is another popular way to manage dependencies in a python environment. 
```
pip install virtualenv
```

cd into the mastergui directory, then:

### 4. VirtualEnv setup
```
virtualenv venv --python=python3
source venv/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt
```

### 5. Running the app in virtualenv
From the command line in the root directory:
 
First activate the virtualenv enviornment:
```
source venv/bin/activate
```

Then run
```
python main.py
```  

### Shortcut for running the virtualenv based installation
The two parts in step 5 are consolidated into a simple shell script that you can use to launch mastergui using virtualenv
```
./go_venv.sh
```

# Configuration
Change config.json.default to config.json and populate with appropriate values for your local environment

By default mastergui will check its root directory for config.json,  however you can also pass in the path to a separate configuration file when launching the app

```
pythin main.py  your_path_to_config_data.json
```

Note: your own private config.json has been added to .gitignore so it will not be updated by git pull

Details on the configuration options are described in the project wiki [here](https://gitlab.com/Fair_lab/mastergui/wikis/configuration)


 
# Tests:
*For Developers.  Normally, mastergui users do not need to run these.*

From the command line in the root directory, activate your conda or virtualenv environment as described above. 

To run all tests
```
pytest tests
```

If pytest is not in your path try
```
python -m pytest tests
```

Helpful testing options include:

specific filename:
```
pytest tests/test_mplus.py
```

 -s to see have stdout show up in your path as well
```
pytest -s tests/
```

-k to run a particular method name
```
