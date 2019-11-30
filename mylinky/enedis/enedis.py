import logging

from .login import Login
from .data import Data

log = logging.getLogger("enedis")

class Enedis:
    RESOURCE = {
        "hourly": Data.RESOURCE_HOURLY,
        "monthly": Data.RESOURCE_MONTHLY,
        "yearly": Data.RESOURCE_YEARLY
    }

    def __init__(self, url=None, url2=None):
        self._login = Login(url)
        self._url2 = url2
        self._cookies = None

    def login(self, username, password):
        cookies = self._login.login(username, password)
        self._cookies = cookies

    def getdata(self, kind, **kwargs):
        h = Data(self._cookies, url=self._url2)
        data = h.get_data(resource=Enedis.RESOURCE[kind], **kwargs)
        log.debug("data (%d): %s%s" % (len(data), data[0:5], "..." if len(data)>6 else ""))
        return data

