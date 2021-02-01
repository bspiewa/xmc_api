from __future__ import print_function

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XmcApi(object):

    def __init__(
            self, host, port=8443, username=None, password=None, client_id=None,
            secret=None):
        """XMC API URLs (based on host and port) and credentials

        Connect to XMC using HTTP Basic Authentication (API user credentials) 
        or HTTP Bearer Authorization (API key - preferred). Constructor calls 
        self._http_oauth() to generate a new token if Bearer Auth is used

        Args:
            host (str): XMC IP address or FQDN
            port (int, optional): XMC NBI listening port. Defaults to 8443.
            username (str, optional): API user login. Defaults to None.
            password (str, optional): API user password. Defaults to None.
            client_id (str, optional): API client ID. Defaults to None.
            secret (str, optional): API secret. Defaults to None.
        """
        self.url = {'nbi': 'https://{0}:{1}/nbi/graphql'.format(host, port)}
        if client_id is None or secret is None:
            self.username = username
            self.password = password
        else:
            self.client_id = client_id
            self.secret = secret
            self.url['oauth'] = (
                'https://{0}:{1}/oauth/token/access-token?'
                'grant_type=client_credentials'.format(host, port))
            self.token = self._http_oauth()

    def _http_basic_auth(self):
        """Access to API user login and password if Basic Authentication

        Returns:
            tuple[str, str]: If login/password exists. Otherwise None
        """
        try:
            auth = self.username, self.password
        except AttributeError:
            auth = None
        return auth

    def _http_oauth(self):
        """Obtain a new token from XMC API

        Raises:
            requests.HTTPError: If token renewal failed

        Returns:
            str: Bearer token
        """
        url = self.url['oauth']  # raises KeyError if BasicAuth
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Cache-Control': 'no-cache',
                   'Accept': 'application/json'}
        r = requests.post(url, verify=False, auth=(
            self.client_id, self.secret), headers=headers)
        if r.ok:
            token = r.json()
        else:
            message = (
                'Bearer Authorization to: {0} using client_id="{1}" '
                'secret="{2}" failed with HTTP Error code: "{3:d}"'.format(
                    url, self.client_id, self.secret, r.status_code))
            raise requests.HTTPError(message)
        return token['access_token']

    def _http_post_headers(self):
        """Set HTTP POST headers

        Returns:
            dict: Dict of required HTTP POST headers
        """
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        try:
            headers['Authorization'] = 'Bearer ' + self.token
        except AttributeError:
            pass
        return headers

    def _cmd(self, cmd):
        """Call XMC NBI using provided command

        Args:
            cmd (str): Graphql query or mutation

        Raises:
            requests.HTTPError: If HTTP Basic Authentication failed

        Returns:
            json: Json server reposnse
        """
        url = self.url['nbi']
        data = {'query': cmd}
        r = requests.post(
            url, verify=False, auth=self._http_basic_auth(),
            headers=self._http_post_headers(),
            json=data)
        code = r.status_code
        if code == requests.codes['unauthorized']:
            try:
                self._http_oauth()  # try to renew token
            except KeyError:
                message = (
                    'Basic Authentication to: {0} with username="{1}" '
                    'password="{2}" failed with code: "{3:d}"'.format(
                        url, self.username, self.password, code))
                raise requests.HTTPError(message)
            else:
                r = requests.post(
                    url, verify=False, headers=self._http_post_headers(),
                    json=data)
                code = r.status_code
        if code == requests.codes['ok']:
            r_content = r.json()
        else:
            r.raise_for_status()
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
    #username = 'apiuser'
    #password = 'password'
    #emc_nbi = XmcApi(host=host, username=username, password=password)
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
