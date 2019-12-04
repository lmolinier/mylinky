import logging
import datetime

from .login import Login
from .data import Data

log = logging.getLogger("enedis")

class Enedis:
    RESOURCE = {
        "hourly": Data.RESOURCE_HOURLY,
        "monthly": Data.RESOURCE_MONTHLY,
        "yearly": Data.RESOURCE_YEARLY
    }

    def __init__(self, url=None, url2=None, timesheets=None):
        self._login = Login(url)
        self._url2 = url2
        self._cookies = None
        self._timesheets = timesheets

    def login(self, username, password):
        cookies = self._login.login(username, password)
        self._cookies = cookies

    @classmethod
    def parsetimesheet(cls, start, end):
        return (datetime.datetime.strptime(start, "%H:%M").time(), datetime.datetime.strptime(end, "%H:%M").time())

    def getdata(self, kind, **kwargs):
        h = Data(self._cookies, url=self._url2, timesheets=self._timesheets)

        # normalize date
        if kind == "monthly":
            kwargs["startDate"] = kwargs["startDate"].replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            kwargs["endDate"] = kwargs["endDate"].replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if kind == "yearly":
            kwargs["startDate"] = kwargs["startDate"].replace(day=1, month=1, hour=0, minute=0, second=0, microsecond=0)
            kwargs["endDate"] = kwargs["endDate"].replace(day=1, month=1, hour=0, minute=0, second=0, microsecond=0)

        log.debug("requesting data (%s): %s - %s" % (kind, kwargs["startDate"], kwargs["endDate"]))
        data = h.get_data(resource=Enedis.RESOURCE[kind], **kwargs)
        log.debug("data (%d): %s%s" % (len(data), data[0:5], "..." if len(data)>6 else ""))
        return data

