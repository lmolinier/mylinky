import yaml
import logging

log = logging.getLogger("config")

class MyLinkyConfig():
    def __init__(self):
        self.data = { 
            "enedis": {
                "user": None,
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
        self.data = data
        return self

    def __getitem__(self, key):
        return self.data[key]

    def override_from_args(self, kwargs):
        # ENEDIS Access
        if "username" in kwargs:
            self.data["enedis"]["user"] = kwargs["username"]
        if "password" in kwargs:
            self.data["enedis"]["password"] = kwargs["password"]

        ## INFLUXDB
        if "host" in kwargs:
            (host,port) = kwargs["host"].split(":")
            self.data["influxdb"]["host"] = host
            self.data["influxdb"]["port"] = port
        if "dbuser" in kwargs:
            self.data["influxdb"]["user"] = kwargs["dbuser"]
        if "dbpassword" in kwargs:
            self.data["influxdb"]["password"] = kwargs["dbpassword"]
        if "db" in kwargs:
            self.data["influxdb"]["database"] = kwargs["db"]
