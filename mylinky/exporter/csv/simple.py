import csv

class CsvExporter:
    def __init__(self, fname, mode):
        self.fname = fname
        self.mode = mode

    def save_data(self, serie, data, batchid=0):
        with open(self.fname, 'w', newline='') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
