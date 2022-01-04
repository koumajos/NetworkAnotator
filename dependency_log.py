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
        "-t",
        help="TCPDUMP row",
        type=str,
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
    reg_ports_tb = load_table_ports(arg.p)

    tmp = arg.t.split()
    ip_s_port_s = tmp[2]
    ip_d_port_d = tmp[4].split(":")[0]

    tmp = ip_s_port_s.split(".")
    port_s = tmp[-1]
    ip_s = ""
    for i in range(len(tmp) - 1):
        if i != len(tmp) - 2:
            ip_s += f"{tmp[i]}."
        else:
            ip_s += tmp[i]

    tmp = ip_d_port_d.split(".")
    port_d = tmp[-1]
    ip_d = ""
    for i in range(len(tmp) - 1):
        if i != len(tmp) - 2:
            ip_d += f"{tmp[i]}."
        else:
            ip_d += tmp[i]

    if len(ip_s.split(":")) > 1:
        return
    tmp_port_s = check_port(int(port_s), reg_ports_tb)
    tmp_port_d = check_port(int(port_d), reg_ports_tb)
    if tmp_port_s is True and tmp_port_d is True:
        id_dependency = f"{ip_d}({port_d})-{ip_s}"
        ip = ip_d
    elif tmp_port_s is True:
        id_dependency = f"{ip_s}({port_s})-{ip_d}"
        ip = ip_s
    elif tmp_port_d is True:
        id_dependency = f"{ip_d}({port_d})-{ip_s}"
        ip = ip_d
    else:
        id_dependency = f"{ip_s}({port_s}-{port_d})-{ip_d}"
        ip = ip_s

    new_row = [id_dependency, ip]
    with open(arg.output_csv, "r") as f:
        existingLines = [line for line in csv.reader(f, delimiter=",")]
        if new_row in existingLines:
            return
    with open(arg.output_csv, "a") as f:
        writer = csv.writer(f)
        writer.writerow(new_row)


if __name__ == "__main__":
    main()
