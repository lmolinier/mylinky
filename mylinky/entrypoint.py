import json
import logging
import boto3
import os

from mylinky import MyLinkyConfig
from mylinky.enedis import Enedis

from base64 import b64decode

# Default logging configuration
logging.basicConfig(format='%(asctime)s %(message)s')  # , datefmt='%m/%d/%Y %I:%M:%S %p')
log = logging.getLogger()
log.setLevel(logging.DEBUG)

BUCKET = "mylinky"
ENEDIS_USER = os.environ["ENEDIS_USER"]
ENEDIS_PASSWORD = os.environ["ENEDIS_PASSWORD"]

def run(events, context):
    response = []

    user = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENEDIS_USER))['Plaintext'].decode()
    password = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENEDIS_PASSWORD))['Plaintext'].decode()
    s3 = boto3.resource("s3")

    # Load the state from s3
    state = json.loads(s3.Bucket(BUCKET).gett_object(Key="state.json"))

    config = MyLinkyConfig()
    config.load_from_dict(events)
    config.override_from_args({"username": user, "password": password})

    enedis = Enedis(timesheets=config["enedis"]["timesheets"])
    enedis.login(config["enedis"]["username"], config["enedis"]["password"])

    #startDate = kwargs["from"]
    #endDate = kwargs["to"]
    #if startDate is None:
    #    delta = args.last
    #    if not delta:
    #        delta = {"hourly": datedelta(days=1), "monthly": datedelta(months=1), "yearly": datedelta(years=1) }[args.type]
    #    startDate = endDate - delta

    #data = enedis.getdata(args.type, startDate=startDate, endDate=endDate)


    # Save the state
    s3.Bucket(BUCKET).put_object(Key="stats.json", Body=json.dumps(state).encode("utf-8"))

    response.append({
        'event': event,
        'statusCode': 200,
        #'body': body[0:1]
    })

    return response