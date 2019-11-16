import logging
import requests
from requests_toolbelt.utils import dump
import base64

log = logging.getLogger("enedis-login")

class LoginException(Exception):
    pass

class Login:
    URL = 'https://espace-client-connexion.enedis.fr/auth/UI/Login'

    def __init__(self, url=None):
        self.url = url if url is not None else Login.URL
        self.session = requests.Session()
        log.debug("Creating login (%s) with session %s" % (self.url, self.session))

    def login(self, username, password):
        self.session.headers.update({'User-agent': "linky crawler"})
        payload = {
            'IDToken1': username,
            'IDToken2': password,
            'SunQueryParamsString': base64.b64encode(b'realm=particuliers'),
            'encoded': 'true',
            'gx_charset': 'UTF-8'
        }

        log.info("Sending login request for user %s" % username)
        resp = self.session.post(self.url, data=payload, allow_redirects=False)

        log.debug("resp: %s" % dump.dump_response(resp).decode('utf-8'))
        log.debug("cookies: %s" % resp.cookies)
        if not 'iPlanetDirectoryPro' in resp.cookies:
            raise LoginException("Login unsuccessful. Check your credentials.")

        return [ c for c in resp.cookies]
