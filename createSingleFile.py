import os, shutil

thisScriptPath = os.path.dirname(os.path.realpath(__file__))

shutil.copy(os.path.join(thisScriptPath, 'src', 'tbmp', '__init__.py'),
            os.path.join(thisScriptPath, 'singleFileVersion', 'tbmp.py'))