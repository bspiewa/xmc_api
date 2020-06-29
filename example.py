from xmc_client import XmcApi

#xmc_api = XmcApi(password='')
xmc_api = XmcApi(client_id='', secret='') #
#data = xmc_api.get_query('{ network { devices { up ip sysName nickName deviceData { vendor family subFamily } } } }')
data = xmc_api.post_query('{ network { devices { up ip sysName nickName deviceData { vendor family subFamily } } } }')
print(data)