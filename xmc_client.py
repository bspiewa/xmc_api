import requests
import urllib3
from xmclib import emc_vars
from xmclib import emc_cli

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class XmcApi(object):
    def __init__(self, xmc_ip=None, xmc_port=None, username=None, password=None, 
        client_id=None, secret=None):
        if xmc_ip is None:
            self.xmc_ip = emc_vars['serverIP']
        else:
            self.xmc_ip = xmc_ip
        if xmc_port is None:
            self.xmc_port = '8443'
        else:
            self.xmc_port = xmc_port
        self.url = {
            'nbi': 'https://{0}:{1}/nbi/graphql'
                .format(self.xmc_ip, self.xmc_port),
            'query': 'https://{0}:{1}/connect/rest/services/nbi/query'
                .format(self.xmc_ip, self.xmc_port),
            'mutation': 'https://{0}:{1}/connect/rest/services/nbi/mutation'
                .format(self.xmc_ip, self.xmc_port),
            'oauth': 'https://{0}:{1}/oauth/token/access-token?' \
                'grant_type=client_credentials'.format(self.xmc_ip, self.xmc_port)
        }
        if client_id is None and secret is None:
            if username is None:
                self.username = emc_vars['userName']
            else:
                self.username = username
            self.password = password
        else:
            self.client_id = client_id
            self.secret = secret
            self.token = self.renew_token()

    def renew_token(self):
        headers = { 
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache',
	        'Accept': 'application/json'
        }
        r = requests.post(self.url['oauth'], verify=False, auth=(self.client_id, 
            self.secret), headers=headers)
        code = r.status_code
        if code == 200:
            token = r.json()
            return token
        else:
            message = 'OAuth to \'{0}\' using CLIENT_ID= \'{1}\' SECRET= \'{2}\' ' \
                'failed with HTTP code: \'{3}\''.format(self.url['oauth'], 
                self.client_id, self.secret, str(code))
            raise Exception(message)

    def http_get_headers(self):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {0}'.format(self.token['access_token']),
                'Accept': 'application/json'
            }
            return headers
        except AttributeError:
            return None

    def http_post_headers(self):
        try:
            headers = {
                'Content-Type': 'application/json', 
                'Authorization': 'Bearer {0}'.format(self.token['access_token']),
                'Accept': 'text/plain'
            }
            return headers
        except AttributeError:
            headers = {
                'Content-Type': 'application/json', 
                'Accept': 'text/plain'
            }
            return headers

    def http_auth(self):
        try:
            auth = (self.username, self.password)
            return auth
        except AttributeError:
            return None

    def get(self, url, params):
        r = requests.get(url, verify=False, auth=self.http_auth(), 
            headers=self.http_get_headers(), params=params)
        code = r.status_code
        if code == 401:
            try:
                self.renew_token()
                r = requests.get(url, verify=False, headers=self.http_get_headers(), 
                    params=params)
                code = r.status_code
            except AttributeError:
                message = 'BasicAuth to \'{0}\' using USERNAME= \'{1}\' PASSWORD= \'{2}\' ' \
                'failed with HTTP code: \'{3}\''.format(url, self.username, self.password, str(code))
                raise Exception(message)
        if code == 200:
            r_content = r.json()
            return r_content
        else:
            message = 'HTTP GET to \'{0}\' failed with code: \'{1}\''.format(url, str(code))
            raise Exception(message)

    def post(self, url, data):
        r = requests.post(url, verify=False, auth=self.http_auth(), 
            headers=self.http_post_headers(), data=data)
        code = r.status_code
        if code == 401:
            try:
                self.renew_token()
                r = requests.post(url, verify=False, headers=self.http_post_headers(), data=data)
                code = r.status_code
            except AttributeError:
                message = 'BasicAuth to \'{0}\' using USERNAME= \'{1}\' PASSWORD= \'{2}\' ' \
                'failed with HTTP code: \'{3}\''.format(url, self.username, self.password, str(code))
        if code == 200:
            r_content = r.json()
            return r_content
        else:
            message = 'HTTP POST to \'{0}\' failed with code: \'{1}\''.format(url, str(code))
            raise Exception(message)

    def get_query(self, query):
        query = 'query=' + query
        r_content = self.get(self.url['nbi'], query)
        return r_content

    def post_query(self, query):
        r_content = self.post(self.url['query'], query)
        return r_content

    def post_mutation(self, mutation):
        r_content = self.post(self.url['mutation'], mutation)
        return r_content
