A user interface to simplify the process of setting up and running a variety of statistical analyses.

The initial version is focused on Mplus so far, but it intended to be a platform to facillitate a variety of platforms. You can think of it as a user-interface to make it easier to configure and run Mplus models. 

See Oscar Miranda-Dominguez, Eric Earl, or David Ball for more info. 

# System Requirements
Python 3

# Installation

pip install packages from requirements.txt

# Configuration
Change config.yml.default to config.yml and populate with appropriate values for your local environment

Note: your own private config.yml has been added to .gitignore so it will not be updated by git pull


# Usage: 

From the command line in the root directory, run: 
```
python main.py
```  
 
# Tests:
From the command line in the root directory, run:
```
pytest tests/
```
Run tests with -s option to see stdout as it processes (i.e. if there are diagnostic print statements in the code)
Use -k your_method_name to test only a specific method in test file.

When running in a virtualenv you may need to run pytest as follows:

```
python -m pytest tests/
```