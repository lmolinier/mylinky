import yaml
import logging

from mylinky.enedis import Enedis

log = logging.getLogger("config")


class MyLinkyConfig():
    def __init__(self):
        self.data = { 
            "enedis": {
                "username": None,
                "password": None,
                "timesheets": None
            },
            "influxdb" : {
                "host": "localhost",
                "port": 8086,
                "database": "linky",
                "username": None,
                "password": None,
                "measurement-prefix": "linky_"
            }
        }

    def _merge(self, d2, d=None):
        if d is None:
            d = self.data
        for (k,v) in d.items():
            if type(d[k])==dict:
                self._merge(d2[k] if k in d2 else {}, d[k])
            elif k in d2:
                if k=="timesheets":
                    d[k] = [ Enedis.parsetimesheet(l[0],l[1]) for l in d2[k] ]
                else:
                    d[k] = d2[k]
        return d

    def load_from_file(self, fname):
        with open(fname) as f:
            data = yaml.load(f)
        log.debug("using configuration: %s" % data)
        self._merge(data)
        log.debug("config: %s" % self.data)
        return self

    def __getitem__(self, key):
        return self.data[key]

    def override_from_args(self, kwargs):
        # ENEDIS Access
        if "username" in kwargs and kwargs["username"] is not None:
            self.data["enedis"]["user"] = kwargs["username"]
        if "password" in kwargs and kwargs["password"] is not None:
            self.data["enedis"]["password"] = kwargs["password"]
        if "timesheet" in kwargs and kwargs["timesheet"] is not None:
            self.data["enedis"]["timesheets"] = kwargs["timesheet"]

        ## INFLUXDB
        if "host" in kwargs and kwargs["host"] is not None:
            (host,port) = kwargs["host"].split(":")
            self.data["influxdb"]["host"] = host
            self.data["influxdb"]["port"] = port
        if "dbuser" in kwargs and kwargs["dbuser"] is not None:
            self.data["influxdb"]["username"] = kwargs["dbuser"]
        if "dbpassword" in kwargs and kwargs["dbpassword"] is not None:
            self.data["influxdb"]["password"] = kwargs["dbpassword"]
        if "db" in kwargs and kwargs["db"] is not None:
            self.data["influxdb"]["database"] = kwargs["db"]

