from __future__ import print_function

import requests
import urllib3

from xmclib import emc_vars  # credentials and IP in emc_vars dictionary

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XmcApi(object):
    def __init__(self, xmc_ip=None, xmc_port=None, username=None,
                 password=None, client_id=None, secret=None):
        if xmc_ip is None:
            xmc_ip = emc_vars['serverIP']
        if xmc_port is None:
            xmc_port = '8443'
        self.url = {
            'nbi': 'https://{0}:{1}/nbi/graphql'.format(xmc_ip, xmc_port),
            'oauth': 'https://{0}:{1}/oauth/token/access-token?'
            'grant_type=client_credentials'.format(xmc_ip, xmc_port)
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
            self.token = self.http_oauth(self.url['oauth'])

    def http_basic_auth(self):
        try:
            auth = self.username, self.password
        except AttributeError:
            auth = None
        return auth

    def http_oauth(self, url):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Cache-Control': 'no-cache',
                   'Accept': 'application/json'}
        r = requests.post(url, verify=False, auth=(
            self.client_id, self.secret), headers=headers)
        code = r.status_code
        if code == 200:
            token = r.json()
        else:
            message = (
                'OAuth to "{0}" using CLIENT_ID="{1}" SECRET="{2}" '
                'failed with HTTP Error code: "{3:d}"'.format(
                    url, self.client_id, self.secret, code))
            raise Exception(message)
        return token['access_token']

    def http_get_headers(self):
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        try:
            headers['Authorization'] = 'Bearer ' + self.token
        except AttributeError:
            pass
        return headers

    def get(self, url, params):
        r = requests.get(url, verify=False, auth=self.http_basic_auth(),
                         headers=self.http_get_headers(), params=params)
        code = r.status_code
        if code == 401:
            try:
                self.http_oauth(self.url['oauth'])
                r = requests.get(
                    url, verify=False, headers=self.http_get_headers(),
                    params=params)
                code = r.status_code
            except AttributeError:
                message = (
                    'BasicAuth to "{0}" with USERNAME="{1}" PASSWORD="{2}" '
                    'failed with HTTP code: "{3:d}"'.format(
                        url, self.username, self.password, code))
                raise Exception(message)
        if code == 200:
            r_content = r.json()
            return r_content
        else:
            message = 'HTTP GET to \'{0}\' failed with code: \'{1}\''.format(
                url, str(code))
            raise Exception(message)

    def query(self, query):
        query = 'query=' + query
        r_content = self.get(self.url['nbi'], query)
        return r_content


if __name__ == '__main__':
    """Self-testing code"""

    emc_nbi = XmcApi(client_id=emc_vars['client_id'], secret=emc_vars['secret'])
    # emc_nbi = XmcApi(password=emc_vars['password'])
    test_query = '''
    {
        network {
            siteByLocation(location: "/World") {
                vlans {
                    name
                    vid
                }
            }
        }
    }
    '''
    result = emc_nbi.query(test_query)
    print(result)
