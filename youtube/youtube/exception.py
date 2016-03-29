'''
Created on Nov 2, 2015

@author: lin
'''

import traceback
import sys

def except_stop():
    exc_type, exc_value, exc_tb = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_tb)
    sys.exit()
