#This script takes a user input UNIX formatted time (epoch format) and outputs a
#human-readable date and time

import datetime

__author__ = 'Raymond Hansen'
__date__ = '20180130'
__version__ = '0.5'

def main():
 """The main function queries the user for a UNIX epoch timestamp and calls
 unix_convert to process the input.
 :return: Nothing."""

def unixConverter(timestamp):
 """The unix_converter function uses the datetime library to convert the timestamp
 :parameter timestamp: An integer representation of a UNIX timestamp.
 :return: A human-readable date & time string."""

 date_ts = datetime.datetime.utcfromtimestamp(timestamp)
 #Use %H for 24 hour format, or %I with %p for 12 hour format with AM/PM
 return date_ts.strftime('%d-%m-%Y %H:%M:%S UTC')

unix_ts = int(input('UNIX timestamp to convert (epoch format): \n >> '))

print (unixConverter(unix_ts))

if __name__ == '__main__': main()