################################################################################
##     This was written for Python3.5+ but may work on lower versions         ##
##         written by Joshua Bulger (jbulger@redhat.com)                      ##
##         November(ish) 2016                                                 ##
################################################################################

# If running RHEL7 or Centos7 install python3 or utilize software collections  #

# Install Software Collections on RHEL7 server:
$ sudo subscription-manager repos --enable rhel-server-rhscl-7-rpms

# Install Software Collections on CentOS 7
$ sudo yum install centos-release-scl

#------------------------------------------------------------------------------#
#                    If using software collections                             #
#------------------------------------------------------------------------------#
# Install required packages
$ sudo yum install scl-utils rh-python35-python{,-{pip,virtualenv}}

# Enable the software collections python environment
$ scl enable rh-python35 bash

#------------------------------------------------------------------------------#
#                   Create the Virtual Environment                             #
#------------------------------------------------------------------------------#
# Enter the dell warranty directory
$ cd dell_warranty

# Create a python virtual environment
$ pyvenv .venv3

# Activate the virtual environment
$ source ./.venv3/bin/activate

# Install the requirements
$ pip install -r ./requirements.txt

#------------------------------------------------------------------------------#
#                            Run the Program                                   #
#------------------------------------------------------------------------------#
(.venv3)...$ ./dell_warranty_info.py --help
usage: dell_warranty_info.py [-h] [-o OUTPUT_FILE] -s
                             [SERIAL_NUMBERS [SERIAL_NUMBERS ...]]

Small program to check Dell Warranty Info by Serial Number

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output file
  -s [SERIAL_NUMBERS [SERIAL_NUMBERS ...]], --serial-numbers [SERIAL_NUMBERS [SERIAL_NUMBERS ...]]
                        list of serial numbers

#------------------------------------------------------------------------------#
#                        Exit the Virtual Environment                          #
#------------------------------------------------------------------------------#
$ deactivate
