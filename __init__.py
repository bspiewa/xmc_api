from xmclib import emc_vars
from .xmc_api import XmcApi
emc_nbi = XmcApi(
    host=emc_vars['serverIP'], client_id=emc_vars['client_id'],
    secret=emc_vars['secret'])
# emc_nbi = XmcApi(
#    host=emc_vars['serverIP'], username=emc_vars['userName'],
#    password=emc_vars['password'])
