#!/usr/bin/python3
"""
create_time_series module:

Crete time series for future analysis from IP flows/biflows.

Copyright (C) 2020 CESNET

LICENSE TERMS

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    3. Neither the name of the Company nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

ALTERNATIVELY, provided that this notice is retained in full, this product may be distributed under the terms of the GNU General Public License (GPL) version 2 or later, in which case the provisions of the GPL apply INSTEAD OF those given above.

This software is provided as is'', and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. In no event shall the company or contributors be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
"""
# Standard libraries imports
import os
import sys
import subprocess
import csv
import argparse
from argparse import RawTextHelpFormatter


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

    # 09:37:48.817004 IP 147.32.76.118.42758 > 3.68.124.168.443: Flags [P.], seq 3734151325:3734151815, ack 1248824436, win 3631, options [nop,nop,TS val 2609698556 ecr 2924979190], length 490

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

    tmp_port_s = check_port(port_s, reg_ports_tb)
    tmp_port_d = check_port(port_d, reg_ports_tb)
    if tmp_port_s is True and tmp_port_d is True:
        id_dependency = f"{ip_d}({port_d})-{ip_s}"
    elif tmp_port_s is True:
        id_dependency = f"{ip_s}({port_s})-{ip_d}"
    elif tmp_port_d is True:
        id_dependency = f"{ip_d}({port_d})-{ip_s}"
    else:
        id_dependency = f"{ip_s}({port_s}-{port_d})-{ip_d}"

    tmp = "False"
    with open(arg.output_csv, "r") as f:
        for line in csv.reader(f, delimiter=","):
            if id_dependency in line[1]:
                tmp = "True"
                break
    exit(tmp)


if __name__ == "__main__":
    main()
