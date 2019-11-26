import unittest
import responses
import logging

from mylinky.enedis import Login, LoginException

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger("test")

class TestLogin(unittest.TestCase):

    @responses.activate
    def testLoginBasic(self):
        l = Login(url="http://testme/login")
        
        responses.add(responses.POST, "http://testme/login", status=302)
        with self.assertRaises(LoginException) as context:
            res = l.login("testuser", "strongpassword")
            log.debug("response: %s" % res)
            self.assertTrue('Login failed' in context.exception)

    @responses.activate
    def testLogin(self):
        l = Login(url="http://testme/login")
        
        responses.add(responses.POST, "http://testme/login", 
            headers={"Set-Cookie": "iPlanetDirectoryPro=AQIC5wM2LY4SfcwzylMnn_BatQOs29LiII_a3kwaYfNSoeE.*AAJTSQACMDIAAlNLABM2Nzg0MDQxNTA0ODQ0ODAzOTg2AAJTMQACMDM.*; Domain=.testme; Path=/"},
            status=302)
        cookies = l.login("testuser", "strongpassword")
        log.debug("auth cookies: %s" % cookies)
        self.assertIsNotNone(cookies)


if __name__ == "__main__":
    unittest.main()