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

from mylinky.enedis import Enedis
from mylinky.exporter import InfluxdbExporter

__all__ = []
__version__ = "UNKNOWN"
__date__ = '2019-11-15'

try:
    __version__ = pkg_resources.get_distribution("linky").version
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
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-v', '--verbose', action='count', default=0, help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        
        group = parser.add_argument_group("importer", "Data importer parameters")
        group.add_argument("--importer", choices=["enedis"], help="select importer [default: %(default)s]", default="enedis")

        enedis = group.add_argument_group("enedis", "ENEDIS Access and Data paremeters")
        enedis.add_argument('-u', '--username', help="Enedis username")
        enedis.add_argument('-p', '--password', help="Enedis password")

        parser.add_argument("--type", choices=[Enedis.HOURLY, Enedis.MONTHLY, Enedis.YEARLY], help="query data source")

        date = parser.add_argument_group("date range", "select the date range")
        date.add_argument("--to", help="to/end query data range (format DD/MM/YYYY)", type=datetime_converter, default=datetime.datetime.now())
        group = date.add_mutually_exclusive_group()
        group.add_argument("--from", help="from/start query date range (format DD/MM/YYYY)", type=datetime_converter)
        group.add_argument("--last", help="query for last days", type=int)

        subparsers = parser.add_subparsers(help='exporter help', dest="exporter")

        subparser = subparsers.add_parser("influxdb", help="Export to InfluxDB")
        subparser.add_argument("--host", default="localhost:8086", help="Database hostname [default: %(default)]")
        subparser.add_argument("--db", required=True, help="Database name")
        subparser.add_argument("--dbuser", required=True, help="Database username")
        subparser.add_argument("--dbpassword", required=True, help="Database password")

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

        enedis = Enedis()
        enedis.login(args.username, args.password)

        startDate = kwargs["from"]
        endDate = kwargs["to"]
        if args.last:
            startDate = endDate - datetime.timedelta(days=args.last)

        data = enedis.getdata(args.type, startDate=startDate, endDate=endDate)

        if args.exporter == "influxdb":
            (host,port) = args.host.split(":")
            influx = InfluxdbExporter(host=host, port=port, database=args.db, username=args.dbuser, password=args.dbpassword)
            influx.save_data("hourly", data)
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
        profile_filename = 'sigfox.sigfox_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    main()
