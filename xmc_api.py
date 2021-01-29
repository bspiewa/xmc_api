from __future__ import print_function

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XmcApi(object):

    def __init__(self, host, port=None, username=None, password=None,
                 client_id=None, secret=None):
        if port is None:
            port = '8443'
        self.url = {'nbi': 'https://{0}:{1}/nbi/graphql'.format(host, port),
                    'oauth': 'https://{0}:{1}/oauth/token/access-token?'
                    'grant_type=client_credentials'.format(host, port)}
        if client_id is None or secret is None:
            self.username = username
            self.password = password
        else:
            self.client_id = client_id
            self.secret = secret
            self.token = self._http_oauth(self.url['oauth'])

    def _http_basic_auth(self):
        try:
            auth = self.username, self.password
        except AttributeError:
            auth = None
        return auth

    def _http_oauth(self, url):
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

    def _http_get_headers(self):
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        try:
            headers['Authorization'] = 'Bearer ' + self.token
        except AttributeError:
            pass
        return headers

    def _cmd(self, cmd):
        url = self.url['nbi']
        data = {'query': cmd}
        r = requests.post(
            url, verify=False, auth=self._http_basic_auth(),
            headers=self._http_get_headers(),
            json=data)
        code = r.status_code
        if code == 401:
            try:
                self._http_oauth(self.url['oauth'])
                r = requests.post(
                    url, verify=False, headers=self._http_get_headers(),
                    json=data)
                code = r.status_code
            except AttributeError:
                message = (
                    'BasicAuth to "{0}" with USERNAME="{1}" PASSWORD="{2}" '
                    'failed with code: "{3:d}"'.format(
                        url, self.username, self.password, code))
                raise Exception(message)
        if code == 200:
            r_content = r.json()
        else:
            message = 'HTTP GET to "{0}" failed with code: "{1:d}"'.format(
                url, code)
            raise Exception(message)
        return r_content['data']

    def query(self, query):
        return self._cmd('query ' + query)

    def mutation(self, mutation):
        return self._cmd('mutation ' + mutation)


if __name__ == '__main__':
    """Self-testing code"""

    host = '10.100.0.40'
    client_id = 'oSfXvoUrfV'
    secret = '1a83fb17-c2bd-46ae-9ee1-9095533740cb'
    emc_nbi = XmcApi(host=host, client_id=client_id, secret=secret)
    # username = apiuser
    # password = testing123
    # emc_nbi = XmcApi(username=username, password=password)
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
