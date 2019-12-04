#!/usr/local/bin/python3
# encoding: utf-8
'''
linky -- Toolbox for dumping data from your French LINKY power counter (from ENEDIS)

It defines classes_and_methods

@author:     lmolinier

@license:    MIT

@contact:    lionel@molinier.eu
@deffield    updated: Updated
'''

import sys
import os
import logging
import pkg_resources
import datetime
import argparse
import pprint

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from mylinky.datedelta import datedelta
from mylinky.enedis import Enedis
from mylinky.exporter import InfluxdbExporter
from mylinky import MyLinkyConfig

__all__ = []
__version__ = "UNKNOWN"
__date__ = '2019-11-15'

try:
    __version__ = pkg_resources.get_distribution("mylinky").version
except pkg_resources.DistributionNotFound:
    pass

# Default logging configuration
logging.basicConfig(format='%(asctime)s %(message)s') #, datefmt='%m/%d/%Y %I:%M:%S %p')
log = logging.getLogger()
log.setLevel(logging.INFO)

DEBUG = 1
TESTRUN = 0
PROFILE = 0

def datetime_converter(s):
    try:
        return datetime.datetime.strptime(s, "%d/%m/%Y")
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid date (DD/MM/YYYY): %s" % s)

def datedelta_converter(s):
    try:
        return datedelta.from_natural_str(s)
    except ValueError:
        raise argparse.ArgumentTypeError("Cannot parse date delta (e.g: '1d', '1m', ...)")

def timesheet_converter(s):
    try:
        (begin,end) = s.split(",")
        return Enedis.parsetimesheet(begin, end)
    except ValueError:
        raise argparse.ArgumentTypeError("Cannot parse timesheet 'time:time', with time '%h:%m'")

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version_message = '%%(prog)s %s' % (__version__)
    program_shortdesc = "LINKY Power consumption toolbox (from ENEDIS)"
    program_license = '''%s

  Created by lmolinier on %s.

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        config = MyLinkyConfig()

        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-v', '--verbose', action='count', default=0, help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-c', "--config", help="configuration file")
        
        group = parser.add_argument_group("importer", "Data importer parameters")
        group.add_argument("--importer", choices=["enedis"], help="select importer [default: %(default)s]", default="enedis")

        enedis = group.add_argument_group("enedis", "ENEDIS Access and Data paremeters")
        enedis.add_argument('-u', '--username', help="Enedis username")
        enedis.add_argument('-p', '--password', help="Enedis password")
        enedis.add_argument("--timesheet", action="append", type=timesheet_converter, help="enter new HP/HC timesheet")

        parser.add_argument("--type", choices=Enedis.RESOURCE.keys(), default="hourly", help="query data source (default: %(default)s)")

        date = parser.add_argument_group("date range", "select the date range")
        date.add_argument("--to", help="to/end query data range (format DD/MM/YYYY)", type=datetime_converter, default=datetime.datetime.now())
        group = date.add_mutually_exclusive_group()
        group.add_argument("--from", help="from/start query date range (format DD/MM/YYYY)", type=datetime_converter)
        group.add_argument("--last", help="query for last days/months/year depending 'type'", type=datedelta_converter)

        subparsers = parser.add_subparsers(help='exporter help', dest="exporter")

        subparser = subparsers.add_parser("influxdb", help="Export to InfluxDB")
        subparser.add_argument("--host", help="Database hostname")
        subparser.add_argument("--db", help="Database name")
        subparser.add_argument("--dbuser", help="Database username")
        subparser.add_argument("--dbpassword", help="Database password")

        subparser = subparsers.add_parser("stdout", help="Export to STDOUT")
        subparser.add_argument("--pretty", help="enable pretty printing")

        args = parser.parse_args()
        kwargs = vars(args)

        log.info('setting log level to {}'.format(args.verbose))
        levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        level = levels[max(0, min(args.verbose-1, len(levels)-1))]
        log.info('effective verbose value set to {}'.format(level))
        logging.getLogger().setLevel(level)

        log.debug("args: %s" % args)
        log.debug("kwargs: %s" % kwargs)
        if args.config:
            config.load_from_file(args.config)
        config.override_from_args(kwargs)
        log.debug("config: %s" % config.data)

        enedis = Enedis(timesheets=config["enedis"]["timesheets"])
        enedis.login(config["enedis"]["username"], config["enedis"]["password"])

        startDate = kwargs["from"]
        endDate = kwargs["to"]
        if startDate is None:
            delta = args.last
            if not delta:
                delta = {"hourly": datedelta(days=1), "monthly": datedelta(months=1), "yearly": datedelta(years=1) }[args.type]
            startDate = endDate - delta

        data = enedis.getdata(args.type, startDate=startDate, endDate=endDate)

        if args.exporter == "influxdb":
            (host,port) = args.host.split(":")
            influx = InfluxdbExporter(
                host=config["influxdb"]["host"], 
                port=config["influxdb"]["port"],
                database=config["influxdb"]["database"],
                username=config["influxdb"]["username"],
                password=config["influxdb"]["password"],
                prefix=config["influxdb"]["measurement-prefix"]
            )

            influx.save_data(args.type, data)
        elif args.exporter == "stdout":
            pprint.pprint(data)

        return 0

    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    return 0

if __name__ == "__main__":
    if DEBUG:
        #sys.argv.append("-h")
        #sys.argv.insert(1, "-v")
        #sys.argv.append("-r")
        pass
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    main()
