#!/usr/bin/python3

# Standard libraries imports
import os
import sys
import csv
import argparse
from argparse import RawTextHelpFormatter
import re
import json


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
    if arg.file is None:
        print("Chrome log file isn't set.")
        sys.exit(1)
    reg_ports_tb = load_table_ports(arg.p)

    if os.path.isfile(arg.file) is False:
        print(f"Chrome log file with name {arg.file} does not exists.")
        sys.exit(2)

    DNS = [
        "dns_query_type",
        "host",
        "network_isolation_key",
        "secure_dns_mode",
        "source_dependency",
    ]
    SOURCE = ["source_dependency"]
    IP = ["local_address", "remote_address"]

    f = open(arg.file)
    data = json.load(f)

    domains = {}
    for event in data["events"]:
        if "params" in event:
            tmp = event["params"].keys()
            if list(tmp) == DNS:
                if event["params"]["host"] not in domains:
                    domains[event["params"]["host"]] = {
                        "id": event["params"]["source_dependency"]["id"],
                    }
            if list(tmp) == SOURCE:
                for domain in domains:
                    if (
                        domains[domain]["id"]
                        == event["params"]["source_dependency"]["id"]
                    ):
                        domains[domain]["id_ip"] = event["source"]["id"]
            if list(tmp) == IP:
                for domain in domains:
                    if (
                        "id_ip" in domains[domain]
                        and domains[domain]["id_ip"] == event["source"]["id"]
                    ):
                        domains[domain]["local_address"] = event["params"][
                            "local_address"
                        ]
                        domains[domain]["remote_address"] = event["params"][
                            "remote_address"
                        ]

    for domain in domains:
        if "local_address" not in domains[domain]:
            continue
        tmp = domains[domain]["local_address"].split(":")
        ip_s = tmp[0]
        port_s = tmp[1]
        tmp = domains[domain]["remote_address"].split(":")
        ip_d = tmp[0]
        port_d = tmp[1]

        tmp_port_s = check_port(int(port_s), reg_ports_tb)
        tmp_port_d = check_port(int(port_d), reg_ports_tb)
        if tmp_port_s is True and tmp_port_d is True:
            domain_id_dependency = f"{ip_d}({port_d})-{ip_s}"
        elif tmp_port_s is True:
            domain_id_dependency = f"{ip_s}({port_s})-{ip_d}"
        elif tmp_port_d is True:
            domain_id_dependency = f"{ip_d}({port_d})-{ip_s}"
        else:
            domain_id_dependency = f"{ip_s}({port_s}-{port_d})-{ip_d}"

        new_row = [domain, domain_id_dependency]
        with open(arg.output_csv, "r") as f:
            existingLines = [line for line in csv.reader(f, delimiter=",")]
            if new_row in existingLines:
                return
        with open(arg.output_csv, "a") as f:
            writer = csv.writer(f)
            writer.writerow(new_row)


if __name__ == "__main__":
    main()
