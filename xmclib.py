
emc_vars = {
    'serverIP': '10.100.0.40', #server IP address - demobox: 192.168.10.30 go: 10.100.0.40
	'serverVersion': 'server version',
	'serverName': 'server host name',
	'time': 'current date at server (yyyy-MM-dd)',
	'date': 'current time at server (HH:mm:ss z)',
    'userName': 'root', # EMC user name
	'userDomain': 'EMC user domain name',
	'auditLogEnabled': 'true/false if audit log is supported',
	'scriptTimeout': 'max script timeout in secs',
	'scriptOwner': 'scripts owner',
	'deviceName': 'DNS name of selected device',
	'deviceIP': '10.100.0.158', #'IP address of the selected device',
	'deviceId': 'device DB ID',
	'deviceLogin': 'login user for the selected device',
	'devicePwd': 'login password for the selected device',
	'deviceSoftwareVer': 'software image version number on the device',
	'deviceType': 'device type of the selected device',
	'deviceSysOid': 'device system object id',
	'deviceVR': 'device virtual router name',
	'cliPort': 'telnet/ssh port',
	'isExos': 'true/false. Is this device an EXOS device?',
	'family': 'device family name',
	'vendor': 'vendor name',
	'deviceASN': 'AS number of the selected device',
	'port': 'selected ports',
	'vrName': 'selected port(s) VR name',
	'ports': 'all device ports',
	'accessPorts': 'all ports which have config role access',
	'interSwitchPorts': 'all ports which have config role interswitch',
	'managementPorts': 'all ports which have config role management'
}

class emc_cli(object):
	def __init__(self):
		pass
	
	@staticmethod
	def send(cmd):
		print cmd
		if cmd is 'show configuration snmp':
			return '#\n# Module snmpMaster configuration.\n#\nconfigure snmpv3 engine-id 03:0c:d8:cb:73:ba:00'
		if cmd is 'show configuration exsshd':
			return '#\n# Module exsshd configuration.\n#'
		else:
			return 'cmdout'