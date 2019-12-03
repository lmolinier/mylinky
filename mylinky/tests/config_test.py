import unittest
import logging
import os

from mylinky import MyLinkyConfig

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
log = logging.getLogger("test")

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = MyLinkyConfig()

    def testLoadSampleYaml(self):
        self.config.load_from_file(os.path.join(os.path.dirname(__file__), "..", "..", "sample", "config.yml"))
        self.assertEqual(self.config["enedis"]["username"], "myenedisuser")
        self.assertEqual(self.config["enedis"]["password"], "myenedispassword")

        self.assertEqual(self.config["influxdb"]["measurement-prefix"], "linky_")

if __name__ == "__main__":
    unittest.main()