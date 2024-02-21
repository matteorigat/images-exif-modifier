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
import numpy as np
from datetime import datetime

# assign directory
directory = '/Users/matteorigat/Desktop/images project/test'

# insert the address to set coordinates it can be an address, a city etc
address = "bormio"  # String or False

# new date  -> if False the old values will remain
new_year = 2024  # like 2023 or False
new_month = 2    # max 12 or False
new_day = 10     # max 31 or False

# new time -> if False the old values will remain
new_hour = False     # max 23 or False
new_minute = False   # max 59 or False
new_second = False   # max 59 or False

# do you want to increment photos timestamps
# to have them in the order in which they are read
# recommended only if you set also the time
increment = False  # in seconds or False


"""

DO NOT EDIT BELOW !!!

"""

EXIF_TAGS = [
    "datetime_original",
    "gps_latitude",
    "gps_latitude_ref",
    "gps_longitude",
    "gps_longitude_ref",
    "gps_altitude",
]

EXIF_ALL_TAGS = ['_exif_ifd_pointer', '_gps_ifd_pointer', 'aperture_value', 'brightness_value', 'color_space',
                 'components_configuration', 'compression', 'datetime', 'datetime_digitized', 'datetime_original',
                 'exif_version',
                 'exposure_bias_value', 'exposure_mode', 'exposure_program', 'exposure_time', 'f_number', 'flash',
                 'flashpix_version', 'focal_length', 'focal_length_in_35mm_film', 'gps_altitude', 'gps_altitude_ref',
                 'gps_datestamp', 'gps_dest_bearing', 'gps_dest_bearing_ref', 'gps_horizontal_positioning_error',
                 'gps_img_direction', 'gps_img_direction_ref', 'gps_latitude', 'gps_latitude_ref', 'gps_longitude',
                 'gps_longitude_ref', 'gps_speed', 'gps_speed_ref', 'gps_timestamp', 'jpeg_interchange_format',
                 'jpeg_interchange_format_length', 'lens_make', 'lens_model', 'lens_specification', 'make',
                 'maker_note',
                 'metering_mode', 'model', 'orientation', 'photographic_sensitivity', 'pixel_x_dimension',
                 'pixel_y_dimension',
                 'resolution_unit', 'scene_capture_type', 'scene_type', 'sensing_method', 'shutter_speed_value',
                 'software',
                 'subject_area', 'subsec_time_digitized', 'subsec_time_original', 'white_balance', 'x_resolution',
                 'y_and_c_positioning', 'y_resolution']

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

    formatted = (float(abs(degrees)), float(minutes), round(seconds, 2))

    return formatted, direction


# Change exif tags
def change_tags(images, lat, lon, alt, dateflag, geoflag):
    increment2 = 0
    changed = False
    for img in images:
        image_path = os.path.join(directory, img)
        with open(image_path, "rb") as input_file:
            exif_img = ExifImage(input_file)

        if dateflag and new_year and new_month and new_day:
            old_date = datetime(1970, 1, 1, 0, 0, 0)
            try:
                old_date = datetime.strptime(exif_img.get("datetime_original"), "%Y:%m:%d %H:%M:%S")
            except:
                print("date in a wrong format")

            if new_year: old_date = old_date.replace(year=new_year)
            if new_month: old_date = old_date.replace(month=new_month)
            if new_day: old_date = old_date.replace(day=new_day)

            if new_hour: old_date = old_date.replace(hour=new_hour)
            if new_minute: old_date = old_date.replace(minute=new_minute)
            if new_second: old_date = old_date.replace(second=new_second)

            if increment:
                old_date = old_date + timedelta(seconds=increment2)
                increment2 += increment

            # old_date = datetime(2020, 1, 1, 0, 0, 0)
            exif_img.datetime = old_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_img.datetime_digitized = old_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_img.datetime_original = old_date.strftime("%Y:%m:%d %H:%M:%S")
            changed = True

        if geoflag and address:
            try:
                exif_img.gps_latitude, exif_img.gps_latitude_ref = convert_coord(lat, True)
                exif_img.gps_longitude, exif_img.gps_longitude_ref = convert_coord(lon, False)
                exif_img.gps_altitude = alt
                changed = True
            except:
                try:
                    exif_img.gps_latitude = lat
                    exif_img.gps_longitude = lon
                    exif_img.gps_altitude = alt
                    changed = True
                except:
                    print("GPS coordinates could not be converted")

        if changed:
            with open(image_path, "wb") as ofile:
                # DANGER ZONE: you are overwriting your photos data
                ofile.write(exif_img.get_file())


# View main data, used most of the time to get a quick overview of the situation
def view_data(images):
    for img in images:
        print(img)
        image_path = os.path.join(directory, img)
        with open(image_path, "rb") as input_file:
            img = ExifImage(input_file)

        for tag in EXIF_TAGS:
            try:
                value = img.get(tag)
                print("{}: {}".format(tag, value))
            except:
                print("Tag {} could not be read".format(tag))
                sys.exit()

        if img.has_exif:
            status = f"contains EXIF (version {img.exif_version}) information."
        else:
            status = "does not contain any EXIF information."
        print(f"Image {status}")
        print("")


# View all exif data, since this print many lines it has as input a single image
def view_first_all_data(img):
    print(img)
    image_path = os.path.join(directory, img)
    with open(image_path, "rb") as input_file:
        img = ExifImage(input_file)

    for tag in EXIF_ALL_TAGS:
        value = img.get(tag)
        if (value is not None):
            print("{}: {}".format(tag, value))


# View only the date of all the images in the directory
def view_all_dates(images):
    for img in images:
        print(img)
        image_path = os.path.join(directory, img)
        with open(image_path, "rb") as input_file:
            img = ExifImage(input_file)

        print("{}: {}".format("datetime_original", img.get("datetime_original")))


if __name__ == '__main__':
    images = []

    # iterate over files in that directory
    read_path(images)

    # view data
    view_data(images)                           # View main data, used most of the time to get a quick overview of the situation
    # view_all_dates(images)                    # View all exif data, since this print many lines it has as input a single
    # image view_first_all_data(images[0])      # View only the date of all the images in the directory

    # Retrieve coordinates
    lat, lon, alt = 0, 0, 0
    if address:
        print("\n")
        address, lat, lon, alt = find_coordinateds()


    # DANGER ZONE: you are overwriting your photos data
    dateflag = input("\nyou are changing the date to \033[93m" + str(new_day) + "/" + str(new_month) + "/" + str(
                      new_year) + "\033[0m are you sure? y/n:\n") == "y"

    geoflag = input("\nyou are changing the location to \033[93m" + str(address) + "\033[0m are you sure? y/n:\n") == "y"


    if dateflag or geoflag:
        change_tags(images, lat, lon, alt, dateflag, geoflag)
        print("\nAFTER\n")
        view_data(images)
