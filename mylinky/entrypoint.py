import json
import logging
import boto3
import os
import tempfile
import datetime
import pytz

from mylinky import MyLinkyConfig
from mylinky.datedelta import datedelta
from mylinky.enedis import Enedis

from base64 import b64decode

# Default logging configuration
logging.basicConfig(format='%(asctime)s %(message)s')  # , datefmt='%m/%d/%Y %I:%M:%S %p')
log = logging.getLogger()
log.setLevel(logging.DEBUG)

BUCKET = "mylinky"
PASSWORD_TYPE = os.environ["PASSWORD_TYPE"] if "PASSWORD_TYPE" in os.environ else "kms"
ENEDIS_USERNAME = os.environ["ENEDIS_USERNAME"] if "ENEDIS_USENAME" in os.environ else None
ENEDIS_PASSWORD = os.environ["ENEDIS_PASSWORD"] if "ENEDIS_PASSWORD" in os.environ else None

def json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()

def run(events, context):
    response = []

    s3 = boto3.resource("s3")
    log.setLevel(logging.getLevelName(events["log"] if "log" in events else "INFO"))

    resource = events["resource"] if "resource" in events else "hourly"
    if PASSWORD_TYPE == "kms":
        username = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENEDIS_USERNAME))['Plaintext'].decode()
        password = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENEDIS_PASSWORD))['Plaintext'].decode()
    elif PASSWORD_TYPE == "s3:clear":
        with tempfile.TemporaryFile() as f:
            s3.Bucket(BUCKET).download_fileobj(Key="creds.json", Fileobj=f)
            f.seek(0)
            creds = json.load(f)
            username = creds["username"]
            password = creds["password"]

    # Load the state from s3
    state = {}
    try:
        with tempfile.TemporaryFile() as f:
            s3.Bucket(BUCKET).download_fileobj(Key="state.json", Fileobj=f)
            f.seek(0)
            state = json.load(f)
    except Exception as e:
        log.info("running with empty sate, because of error: %s" % e)
    if resource not in state:
        state[resource] = {}

    if "state" in events:
        state.update(events["state"])
    log.info("State: %s" % state)

    # Load configuration
    config = MyLinkyConfig()
    try:
        with tempfile.TemporaryFile() as f:
            s3.Bucket(BUCKET).download_fileobj(Key="config.yml", Fileobj=f)
            f.seek(0)
            config.load_from_fileobj(f)
    except Exception as e:
        log.info("running with empty config, because of error: %s" % e)

    config.load_from_dict(events)
    config.override_from_args({"username": username, "password": password})
    log.info("Configuration: %s" % config.data)

    enedis = Enedis(timesheets=config["enedis"]["timesheets"])
    enedis.login(config["enedis"]["username"], config["enedis"]["password"])

    startDate = datetime.datetime.strptime(state[resource]["last"], "%d/%m/%Y").replace(tzinfo=pytz.timezone("Europe/Paris"))+datedelta(days=1) if "last" in state[resource] else None
    endDate = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0,tzinfo=pytz.timezone("Europe/Paris"))
    if startDate is None:
        # Max retention in ENEDIS is 1 year
        startDate = endDate - datedelta(years=1)
    if startDate == endDate:
        response.append({
            'error': "same date start/end %s" % endDate
        })
        return response
    
    data = enedis.getdata(resource, startDate=startDate, endDate=endDate)

    if len(data) and startDate == data[0]["date"]:
        s3.Bucket(BUCKET).put_object(Key="%s/%s.json" % (resource, endDate.strftime("%Y-%m-%d")), Body=json.dumps(data, default=json_converter).encode("utf-8"))

        # Save the state
        lastDate = data[-1]["date"]
        state[resource]["last"] = lastDate.strftime("%d/%m/%Y")
        s3.Bucket(BUCKET).put_object(Key="state.json", Body=json.dumps(state).encode("utf-8"))

    response.append({
        'startDate': str(startDate),
        'endDate': str(endDate),
        'items': len(data)
    })

    return response