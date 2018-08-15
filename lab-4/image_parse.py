####################################################################################################
# Program:      Image Parser
# Author:       Jake Mathews
# Date:         July 27th, 2018
# Description:  The user provides a path to either a path to a directory containing images or a path
#               to an tar archive containing images. The program will extract information about the
#               image and display is. If the user provides the path to a text file containing the
#               hashes of images known to be illicit, or one can be found in the current working
#               directory, then the program will hash the images found and compare them to the list.
####################################################################################################

from PIL import Image
from PIL import ExifTags
import argparse
from os import stat
from pwd import getpwuid
import os
import hashlib
import tarfile

# Print statement tags
info_tag = '[INFO]'
warning_tag = '[WARNING]'
error_tag = '[ERROR]'


# Utility function for getting file owner
def find_owner(file_path):
    return getpwuid(stat(file_path).st_uid).pw_name


# Define and parse arguments
parser = argparse.ArgumentParser(description='Read exif data on jpeg images')
parser.add_argument('-a', '--archive', type=str, nargs='?',
                    help='path to the tar file containing images')
parser.add_argument('-d', '--directory', type=str, nargs='?',
                    help='path to the directory containing images.'
                         ' this will be used in the case that the archive argument is also provided')
parser.add_argument('-l', '--list', type=str, nargs='?',
                    help='path to hash list text file. default is file name \'hash_list.txt\'')
parser.add_argument('-v', '--verbose', action="store_true",
                    help='display extra logging information')
args = parser.parse_args()

# Determine logging level
verbose = args.verbose

# Define default directory
directory = os.path.abspath('images/')

# Open archive
archive_path = 'images.tgz'
if args.archive:
    if os.path.exists(args.archive) and os.path.isfile(args.archive):
        archive_path = os.path.abspath(args.archive)
    else:
        print(warning_tag, 'Provided path does not exist or is not a file')
        exit(1)

if not os.path.exists(directory) and os.path.exists(archive_path) and os.path.isfile(archive_path):
    tar = tarfile.open(archive_path, "r:gz")
    tar.extractall()
    tar.close()
else:
    print(warning_tag, 'No hash list found. Cannot check if content is illicit')

# Determine directory to search in
if args.directory:
    if os.path.exists(args.directory) and os.path.isdir(args.directory):
        directory = os.path.abspath(args.directory)
    else:
        print(warning_tag, 'Provided path does not exist or is not a directory')
        exit(2)

# Determine hash list to compare against
hash_list_path = 'hash_list.txt'
hash_list = []
if args.list:
    if os.path.exists(args.list) and os.path.isfile(args.list):
        hash_list_path = os.path.abspath(args.list)
    else:
        print(warning_tag, 'Provided path for list does not exist or is not a file')
        exit(3)

if os.path.exists(hash_list_path) and os.path.isfile(hash_list_path):
    hash_list = open(hash_list_path, "rb").read().splitlines()
else:
    print(warning_tag, 'No hash list found. Cannot check if content is illicit')
if verbose:
    print(info_tag, hash_list)

# Walk directory in search of images
paths = []
print(info_tag, 'Searching for images in ', directory, '\n')
for _, _, file_names in os.walk(directory):
    for (filename) in file_names:
        path = os.path.join(directory, filename)
        paths.append(path)
    break

# Gather and print data from each image found
for path in paths:
    try:
        # Try to open image
        image = Image.open(path)

        # Gather Exif data
        exif = {}
        # noinspection PyProtectedMember
        if image._getexif():
            # noinspection PyProtectedMember
            exif = {
                ExifTags.TAGS[k]: v
                for k, v in image._getexif().items()
                if k in ExifTags.TAGS
            }

        # Hash Image
        image_hash = hashlib.md5()
        with open(path, 'rb') as image_file:
            buffer = image_file.read()
            image_hash.update(buffer)
        image_hash = image_hash.hexdigest().encode('UTF-8')

        if verbose:
            print(info_tag, 'Image Hash:', image_hash)

        # Gather image data
        image_data = {}
        if len(hash_list) > 0:
            image_data['Illicit'] = image_hash in hash_list

        image_data['Image Name'] = os.path.basename(image.filename)
        image_data['Path'] = image.filename
        image_data['Size (WxH)'] = image.size
        image_data['Owner'] = find_owner(image.filename)

        if 'Make' in exif:
            image_data['Camera Make'] = exif['Make']
        if 'Model' in exif:
            image_data['Camera Model'] = exif['Model']
        if 'DateTimeOriginal' in exif:
            image_data['Date'] = exif['DateTimeOriginal']
        if 'GPSInfo' in exif:
            gps = {
                ExifTags.GPSTAGS[k]: v
                for k, v in exif['GPSInfo'].items()
                if k in ExifTags.GPSTAGS
            }


            def add_gps_info(tag1, tag2):
                if tag1 in gps and tag2 in gps:
                    image_data[tag1] = str(gps[tag1]) + str(gps[tag2])


            add_gps_info('GPSLatitude', 'GPSLatitudeRef')
            add_gps_info('GPSLongitude', 'GPSLongitudeRef')

            if 'GPSDateStamp' in gps:
                image_data['GPS DateStamp'] = gps['GPSDateStamp']

            if verbose:
                image_data['Raw GPSInfo'] = gps

        if verbose:
            image_data['Raw Exif'] = exif

        # Display image data
        maxLength = 15
        for data_name, data in image_data.items():
            print(data_name.ljust(maxLength) + ':', str(data))

        print('')
        # do stuff
    except IOError:
        # filename not an image file
        if verbose:
            print(error_tag, 'Not an image: ', path)
