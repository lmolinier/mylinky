from influxdb import InfluxDBClient

class InfluxdbExporter:
    def __init__(self, **kwargs):
        self.client = InfluxDBClient(**kwargs)

    def connect(self):
        pass

    def save_data(self, serie, data, batchid=0):
        d = []
        for item in data:
            d.append({
                "measurement": serie,
                "tags": {
                    "batchid" : batchid,
                    "type" : item["type"],
                },
                "time": item['date'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "value": (item['value']*1000),
                    "price": (item['price']),
                }
            })

        self.client.write_points(d)
        return len(d)