#!/usr/bin/python3

# Standard libraries imports
import os
import sys
import subprocess
import csv
import argparse
from argparse import RawTextHelpFormatter
import glob
import re


def ports_convert_to_int(port):
    try:
        return int(port)
    except:
        return port


def load_table_ports(filename):
    """Load ports table, that contain ports registered by IANA and ICANN, from csv and return it as dictionary.

    Returns:
        dictionary: Loaded ports table as a dictionary (port->service_name).
    """
    if filename.endswith(".csv") is False:
        print("The filename of table contains services haven't suffix or isn't .csv")
        sys.exit(1)
    if os.path.isfile(filename) is False:
        print(f"The file with name {filename} doesn't exists.")
        sys.exit(1)
    try:
        with open(filename, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            reg_ports = dict(
                (ports_convert_to_int(rows[1]), rows[0]) for rows in reader
            )
        return reg_ports
    except:
        print(f"Error in loading file {filename}")
        sys.exit(1)


def check_port(port, ports_tb):
    """Check if port used in dependency is service or registered.

    Args:
        port (int): Integer of used port by device.
        services_tb (dictionary): Dictionary contains list of services.
        ports_tb (dictionary): Dictionary contains registered port defined by IANA and ICAN.

    Returns:
        bool: True if port is service or registered.
    """
    if ports_tb.get(port) is not None:
        if ports_tb.get(port) == "":
            return False
        return True
    return False


def parse_arguments():
    """Function for set arguments of module.

    Returns:
        argparse: Return setted argument of module.
    """
    parser = argparse.ArgumentParser(
        description="""

    Usage:""",
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument(
        "-d",
        "--dir",
        help="Directory to log files.",
        type=str,
        metavar="PATH",
        default=None,
    )

    parser.add_argument(
        "-f",
        "--file",
        help="Log file.",
        type=str,
        metavar="FILE",
        default=None,
    )

    parser.add_argument(
        "-c",
        "--output_csv",
        help="Output CSV for safe data. Default it's output.csv.",
        type=str,
        metavar="NAME.SUFFIX",
        default="output.csv",
    )

    parser.add_argument(
        "-l",
        "--dependency_log",
        help="Dependenycy log file.",
        type=str,
        metavar="FILE",
        default=None,
    )

    parser.add_argument(
        "-p",
        help="Set the name with suffix of file, where are safe registered ports (default: Ports.csv). File must be .csv",
        type=str,
        metavar="NAME.SUFFIX",
        default="Ports.csv",
    )

    arg = parser.parse_args()
    return arg


def main():
    """Main function of the module."""
    arg = parse_arguments()
    if arg.dir is None and arg.file is None:
        print("Firefox log file of directory to firefox log files isn't set.")
        sys.exit(1)

    if arg.dir is not None:
        filePaths = glob.glob(os.path.join(arg.dir, "log.txt*".format("identifier")))
    else:
        if os.path.isfile(arg.file) is True:
            filePaths = [arg.file]
        else:
            filePaths = []

    with open(arg.dependency_log, "r") as f:
        ip_dependencies = [line for line in csv.reader(f, delimiter=",")]

    for log_file in filePaths:
        with open(log_file, "r") as f:
            text = f.read()
        text = text.split("\n")
        for i in range(len(text)):
            if re.search("\d+\.\d+\.\d+\.\d+", text[i]):
                s = text[i].split(" has ")
                ip = s[-1]
                for i in range(len(ip_dependencies)):
                    if ip == ip_dependencies[i][1]:
                        domain = s[-2].split(": ")[-1]
                        new_row = [domain, ip_dependencies[i][0]]
                        with open(arg.output_csv, "r") as f:
                            existingLines = [
                                line for line in csv.reader(f, delimiter=",")
                            ]
                            if new_row in existingLines:
                                continue
                        print(new_row)
                        with open(arg.output_csv, "a") as f:
                            writer = csv.writer(f)
                            writer.writerow(new_row)


if __name__ == "__main__":
    main()
