#!/usr/bin/env python3

import os.path
from datetime import datetime
import argparse
import json
import csv
import sys
import logging
import grequests
from bs4 import BeautifulSoup


def parse_args():
    parser = argparse.ArgumentParser(description='Small program to check Dell Warranty Info by Serial Number')
    parser.add_argument("-o", "--output-file", nargs=1,help="Output file", required=False)
    parser.add_argument("-l", "--limit-requests", nargs=1, help="Rate limit requests",
                        type=int, default=100, required=False)
    parser.add_argument("-L", "--Log", nargs=1, help="Log File",
                        default='/tmp/dell_warranty_checker.log', required=False)
    parser.add_argument("-s", "--serial-numbers", nargs='*', help="list of serial numbers", required=True)
    return parser.parse_args()

def get_urls (base_url, serials_numbers, size = 100):
    response_futures = (grequests.get(str(base_url) + str(sn)) for sn in serials_numbers)
    responses = grequests.imap(response_futures, size = size) #
    return responses

def parse_response (response):
    # Grab all class objects from html matching below
    bsObj = BeautifulSoup(response.text, "html.parser").findAll("div", {"class":{"WarrantyInformation"}})
    # Set infomation dictionary based on list comprehension of above (first object was '')
    info = {x[1].replace(":",""):x[2] for x in [ line.get_text().splitlines() for line in bsObj]}
    # Update date with desired format ('2013-10-23T00:00:00-05:00' => '2013-10-23')
    info.update({x:info[x].split("T")[0] for x in info.keys() if "Date" in x})
    # Insert Serial Number into dictionary
    info['Serial Number'] = response.url[response.url.rfind("/")+1:]
    # Fix format as requsted by DRohwer
    info['Provider'] = 'Dell' if (info['Provider'].lower() == 'uny') else info['Provider'].title()
    return info

def writeCSV(out_file, systems):
    KEYS = {x for y in systems for x in y.keys()}
    with open(out_file, 'xt') as f:
        w = csv.DictWriter(f, fieldnames=KEYS)
        w.writeheader()
        w.writerows(systems)

def writeJSON(out_file, systems):
    with open(out_file, 'xt') as f:
        json.dump(systems, f)

def main():
    systems = []
    args = parse_args()
    logging.basicConfig(filename=args.Log,level=logging.DEBUG)

    for r in get_urls("https://qrl.dell.com/",args.serial_numbers, args.limit_requests):
        try:
            systems.append(parse_response(r))
            print("Found System Information for: ", str(systems[-1]['Serial Number']))
        except AttributeError as e:
            print( "Error : %s Not Found" % r.url[r.url.rfind("/")+1:])
            logging.error("Error: %s" % r.url[r.url.rfind("/")+1:])

# If there's a file to write to, else output json
    if (args.output_file):
        if (os.path.isfile(args.output_file[0])):
            output_file = "Dell-Warranty-Status-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".csv"
            print("%s already exists - writing output to %s instead." % str(args.output_file[0]), output_file)
            writeCSV(output_file , systems)
        else:
            if (args.output_file[0].split(".")[-1].lower() == "json") or (args.output_file[0].split(".")[-1].lower() == "jsn"):
                try:
                    writeJSON(args.output_file[0], systems)
                    print ("Wrote output to file: %s" % str(args.output_file[0]) )
                except AttributeError as e:
                    logging.error(e)
                    writeJSON("Dell-Warranty-Status-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".json", systems)
            else:
                if (args.output_file[0].split(".")[-1].lower() != "csv"):
                    args.output_file[0] = args.output_file[0] + ".csv"
                try:
                    writeCSV(args.output_file[0], systems)
                    print ("Wrote output to file: %s" % str(args.output_file[0]) )
                except AttributeError as e:
                    logging.error(e)
                    writeCSV("Dell-Warranty-Status-" + datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".csv" , systems)
    else:
        print(json.dumps(systems, sort_keys=True, indent=4))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
