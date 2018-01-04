A user interface to simplify the process of setting up and running a variety of statistical analyses.

The initial version is focused on Mplus so far, but it intended to be a platform to facillitate a variety of platforms. You can think of it as a user-interface to make it easier to configure and run Mplus models. 

See Oscar Miranda-Dominguez, Eric Earl, or David Ball for more info. 

# System Requirements
Python 3

# Installation

pip install packages from requirements.txt

The MatLab Python API needs to be installed separately from PIP

After activating your virtualenv at the command line, cd to your "{matlabroot}\extern\engines\python"
and run:

```
python setup.py build - -build - base = "{replace_with_path_to_your_mastergui_installation}/venv/build" install
```

# Configuration
Change config.yml.default to config.yml and populate with appropriate values for your local environment

Note: your own private config.yml has been added to .gitignore so it will not be updated by git pull


# Usage: 

From the command line in the root directory:
 
First activate the virtualenv enviornment:
```
source venv/bin/activate
```

Then run
```
python main.py
```  
 
# Tests:
From the command line in the root directory

First activate the virtualenv enviornment:
```
source venv/bin/activate
```
Then run all tests
```
pytest tests
```

If pytest is not in your path try
```
python -m pytest tests
```

Helpful options include:

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
