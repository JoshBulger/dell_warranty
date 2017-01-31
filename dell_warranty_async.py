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
                        type=int, default=10, required=False)
    parser.add_argument("-L", "--Log", nargs=1, help="Log File",
                        default='/tmp/dell_warranty_checker.log', required=False)
    parser.add_argument("-s", "--serial-numbers", nargs='*', help="list of serial numbers", required=True)
    return parser.parse_args()

def get_urls (base_url, serials_numbers, size = 100):
    response_futures = (grequests.get(str(base_url) + str(sn)) for sn in serials_numbers)
    responses = grequests.imap(response_futures, size = size) #
    return responses

def parse_response (response):
    info = {}
    if response.status_code == 200:
        info['Serial_Number'] = response.url[response.url.rfind("/")+1:]
        print("Found System Information for: ", str(info['Serial_Number']))
        bsObj = BeautifulSoup(response.text, "html.parser")
        details = [line for line in bsObj.find("div", {"class":{"descriptionTxt"}}).findAll("p")[1].get_text().splitlines() if line.strip()]
        for x in details:
            k = x.split(': ')[0].replace(" ","_")
            v = x.split(': ')[1]
            if "date" in k.lower():
                v = v[:v.find("T")]
            info[k] = v
        return info
    else:
        print("Coundn't Find System Information for: ", str(info['Serial_Number']))

def writeCSV(out_file, systems):
    with open(out_file, 'xt') as f:
        w = csv.writer(f)
        w.writerow(systems[0].keys())
        for x in systems:
            w.writerow(x.values())

def writeJSON(out_file, systems):
    with open(out_file, 'xt') as f:
        json.dump(systems, f)

def main():
    systems = []
    args = parse_args()
    logging.basicConfig(filename=args.Log,level=logging.DEBUG)

    for r in get_urls("https://qrl.dell.com/",args.serial_numbers, args.limit_requests[0]):
        try:
            x = parse_response(r)
            systems.append(x)
            logging.info("Success : %s" % x['Serial_Number'])
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
