import yaml
import logging

log = logging.getLogger("config")

class MyLinkyConfig():
    def __init__(self):
        self.data = { 
            "enedis": {
                "username": None,
                "password": None
            },
            "influxdb" : {
                "host": "localhost",
                "port": 8086,
                "database": "linky",
                "user": None,
                "password": None
            }
        }

    def load_from_file(self, fname):
        with open(fname) as f:
            data = yaml.load(f)
        log.debug("using configuration: %s" % data)
        self.data.update(data)
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

        ## INFLUXDB
        if "host" in kwargs and kwargs["host"] is not None:
            (host,port) = kwargs["host"].split(":")
            self.data["influxdb"]["host"] = host
            self.data["influxdb"]["port"] = port
        if "dbuser" in kwargs and kwargs["dbuser"] is not None:
            self.data["influxdb"]["user"] = kwargs["dbuser"]
        if "dbpassword" in kwargs and kwargs["dbpassword"] is not None:
            self.data["influxdb"]["password"] = kwargs["dbpassword"]
        if "db" in kwargs and kwargs["db"] is not None:
            self.data["influxdb"]["database"] = kwargs["db"]
