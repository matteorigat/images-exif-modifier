import os
import ssl
import sys
from datetime import datetime, timedelta
import certifi
# importing geopy library and Nominatim class
import geopy.geocoders
import requests
from exif import Image as ExifImage
import piexif
from PIL import Image

# assign directory
directory = '/Users/matteorigat/Desktop/images project/myimages'

# insert the address to set coordinates it can be an address, a city etc
address = "Livigno"  # String or False

# new date  -> if False the old values will remain
new_year = 2004  # like 2023 or False
new_month = 1    # max 12 or False
new_day = 22     # max 31 or False

# new time -> if False the old values will remain
new_hour = False     # max 23 or False
new_minute = False   # max 59 or False
new_second = False   # max 59 or False

# do you want to increment photos timestamps?
# to have them in the order in which they are read
# please note that the photos will be ordered alphabetically
# recommended only if you set also the time
increment = False  # in seconds or False


"""

DO NOT EDIT BELOW !!!

"""


TAG = [
    'Make',
    'Model',
    'DateTime',
    'DateTimeOriginal',
    'DateTimeDigitized',
    'GPSVersionID',
    'GPSLatitude',
    'GPSLatitudeRef',
    'GPSLongitude',
    'GPSLongitudeRef',
    'GPSAltitude',
    'GPSAltitudeRef',
    'GPSDateStamp'
]

# Iterate over files in the directory to select only photos
def read_path(images):
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)

        # Skip directories
        if os.path.isdir(full_path):
            print(f"Skipping directory: {full_path}")
            continue

        # Skip videos, maybe in the future i'll implement a video modifier
        if any(filename.lower().endswith(i) for i in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']):
            print('\033[91m' + f"video file found: {full_path}" + '\033[0m')
        elif any(filename.lower().endswith(i) for i in
                 ['.jpg', '.jpeg', '.jfif', '.tiff', '.tif', '.png', '.gif', '.webp', ".bmp", ".heif", ".heic", ]):
            # Add image files to the list
            images.append(filename)
    # order alphabetically
    images.sort()


# Retrieve latitude, longitude and altitude from an address
def find_coordinateds():
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    # calling the Nominatim tool and create Nominatim class
    geolocator = geopy.Nominatim(user_agent="images_editor")
    location = geolocator.geocode(address)

    print("Location found:\n" + location.address)
    lat = location.latitude
    lon = location.longitude
    url = f"https://api.opentopodata.org/v1/aster30m?locations={lat},{lon}"
    r = requests.get(url)
    data = r.json()
    alt = data['results'][0]['elevation']
    print(lat, lon, alt)
    print(convert_coord(lat, True))
    print(convert_coord(lon, False))
    # check https://coordinates-converter.com/
    return location.address, lat, lon, alt


# Recent photos apps use coordinates in degrees
def convert_coord(x, check):
    degrees = int(x)
    minutes = int((x - degrees) * 60)
    seconds = (x - degrees - minutes / 60) * 3600
    if (check):
        direction = "N" if degrees >= 0 else "S"
    else:
        direction = "E" if degrees >= 0 else "W"

    accuracy = 100  # integer greater than 1, it is a denominator
    formatted = [(abs(degrees), 1), (minutes, 1), (int(seconds*accuracy), accuracy)]

    return formatted, direction


# Change exif tags
def change_date(images):
    increment2 = 0
    changed = False
    for img in images:
        image_path = os.path.join(directory, img)
        new_img = Image.open(image_path)

        try:
            exif_dict = piexif.load(new_img.info['exif'])
        except KeyError:
            exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}

        if new_year and new_month and new_day:
            old_date = datetime(1970, 1, 1, 0, 0, 0)
            try:
                old_date = datetime.strptime(exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode(), "%Y:%m:%d %H:%M:%S")
            except:
                print("date in a wrong format")
                if input("Do you want to continue? y/n:\n") != "y":
                    sys.exit()


            if new_year: old_date = old_date.replace(year=new_year)
            if new_month: old_date = old_date.replace(month=new_month)
            if new_day: old_date = old_date.replace(day=new_day)

            if new_hour: old_date = old_date.replace(hour=new_hour)
            if new_minute: old_date = old_date.replace(minute=new_minute)
            if new_second: old_date = old_date.replace(second=new_second)

            if increment:
                old_date = old_date + timedelta(seconds=increment2)
                increment2 += increment

            exif_dict['0th'][piexif.ImageIFD.DateTime] = old_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = old_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = old_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_dict['GPS'][piexif.GPSIFD.GPSDateStamp] = old_date.strftime("%Y:%m:%d")
            changed = True

        if changed:
            # DANGER ZONE: you are overwriting your photos data
            exif_bytes = piexif.dump(exif_dict)
            new_img.save(image_path, exif=exif_bytes)

def change_coords(images, lat, lon, alt):

    for img in images:
        image_path = os.path.join(directory, img)
        new_img = Image.open(image_path)

        try:
            exif_dict = piexif.load(new_img.info['exif'])
        except KeyError:
            exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}

        # Set GPS Info
        exif_dict['GPS'][piexif.GPSIFD.GPSVersionID] = (2, 2, 0, 0)
        exif_dict['GPS'][piexif.GPSIFD.GPSLatitude], exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = convert_coord(lat, True)
        exif_dict['GPS'][piexif.GPSIFD.GPSLongitude], exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = convert_coord(lon, False)
        exif_dict['GPS'][piexif.GPSIFD.GPSAltitude], exif_dict['GPS'][piexif.GPSIFD.GPSAltitudeRef] = (int(alt*100), 100), 0

        # DANGER ZONE: you are overwriting your photos data
        exif_bytes = piexif.dump(exif_dict)
        new_img.save(image_path, exif=exif_bytes)


def view_data(images):
    for img in images:
        print("\033[93m" + img + "\033[0m")
        image_path = os.path.join(directory, img)
        new_img = Image.open(image_path)
        try:
            exif_dict = piexif.load(new_img.info['exif'])
        except Exception as e:
            print(e)

        for ifd in ("0th", "Exif", "GPS", "1st"):
            for tag in exif_dict[ifd]:
                if piexif.TAGS[ifd][tag]["name"] in TAG:
                    print(piexif.TAGS[ifd][tag]["name"], exif_dict[ifd][tag])
        print("")

def print2(images):
    for img in images:
        image_path = os.path.join(directory, img)
        exif_dict = piexif.load(image_path)

        # Extract thumbnail and save it, if exists
        thumbnail = exif_dict.pop('thumbnail')
        if thumbnail is not None:
            with open('thumbnail.jpg', 'wb') as f:
                f.write(thumbnail)

        # Iterate through all the other ifd names and print them
        print(f'Metadata for {img}:')
        for ifd in exif_dict:
            print(f'{ifd}:')
            for tag in exif_dict[ifd]:
                tag_name = piexif.TAGS[ifd][tag]["name"]
                tag_value = exif_dict[ifd][tag]
                # Avoid print a large value, just to be pretty
                if isinstance(tag_value, bytes):
                    tag_value = tag_value[:10]
                print(f'\t{tag_name:25}: {tag_value}')
        print()




if __name__ == '__main__':
    images = []

    # iterate over files in that directory
    read_path(images)

    # view data
    view_data(images)

    # Retrieve coordinates
    if address:
        print("\n")
        address, lat, lon, alt = find_coordinateds()


    # DANGER ZONE: you are overwriting your photos data
    dateflag = input("\nyou are changing the date to \033[93m" + str(new_day) + "/" + str(new_month) + "/" + str(
                      new_year) + "\033[0m are you sure? y/n:\n") == "y"

    geoflag = input("\nyou are changing the location to \033[93m" + str(address) + "\033[0m are you sure? y/n:\n") == "y"


    if dateflag:
        change_date(images)
    if geoflag and address:
        change_coords(images, lat, lon, alt)

    if (dateflag or geoflag) and  input("\nprint output? y/n:\n") == "y":
        print("\nAFTER\n")
        view_data(images)
