from xmclib import emc_vars
from .xmc_api import *
emc_nbi = XmcApi(client_id=emc_vars['client_id'], secret=emc_vars['secret'])