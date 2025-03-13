"""
IC-ENC utils __init__.py

Script ran when the utils.py package is used, it reorders all sub-packages 
so that it can be accessed from the top-level and avoid complex imports.


Author: AJW

last amended: AJW 03/02/2025

date: 03/02/2025

v1.0

"""


## import sub module functions

if __name__ == "__main__":
    # absolute imports if this script is ran explicitly
    from utils.autoclassifications import *
    from utils.get_S57_overlaps import *
    from utils.imports57 import *
    from utils.imports101 import *
    from utils.static_vars import *

    print("utils.__init__.py has been ran directly, please review if this was done deliberately")

else:
    # relative imports when imported from main.py
    from .autoclassifications import *
    from .get_S57_overlaps import *
    from .imports57 import *
    from .imports101 import *
    from .static_vars import *


# end of script