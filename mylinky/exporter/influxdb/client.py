from influxdb import InfluxDBClient

class InfluxdbExporter:
    def __init__(self, **kwargs):
        self.prefix = kwargs["prefix"]
        del kwargs["prefix"]
        self.client = InfluxDBClient(**kwargs)

    def connect(self):
        pass

    def save_data(self, serie, data, batchid=0):
        d = []
        for item in data:
            d.append({
                "measurement": "%s%s"% (self.prefix, serie),
                "tags": {
                    "batchid" : batchid
                },
                "time": item['date'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "value": (item['value']*1000),
                    "duration": item['duration']
                }
            })

        self.client.write_points(d)
        return len(d)