
if __name__ == "__main__":
    # absolute imports if this script is ran explicitly
    from reformat_qgis_inputs import *


    print("utils.__init__.py has been ran directly, please review if this was done deliberately")

else:
    # relative imports when imported from main.py
    from .reformat_qgis_inputs import *


