import os
from datetime import datetime, timedelta
from exif import Image as ExifImage
# importing geopy library and Nominatim class
import geopy.geocoders
import ssl
import certifi
import requests


# assign directory
directory = '/Volumes/SanDisk/Matteo/Foto Matteo completo redated/2002 estate/castiglione/agosto'

#insert the city to set coordinates
city = "Roccamare"  # String or False

# new date  -> if False the old value will remain
new_year = 2002  # like 2023 or False
new_month = 8  # max 12 or False
new_day = 20  # max 31 or False

new_hour = False  # max 23 or False
new_minute = False  # max 59 or False
new_second = False  # max 59 or False

# do you want to increment photos timestamps
# to have them in the order in which they are read
# recommended only if you set also the time
increment = False  # in seconds or False


"""

DO NOT EDIT BELOW !!!

"""


EXIF_TAGS = [
     #"make",
     #"model",
     #"datetime",
     #"datetime_digitized",
     "datetime_original",
     "gps_latitude",
     #"gps_latitude_ref",
     "gps_longitude",
     #"gps_longitude_ref",
     "gps_altitude",
]


EXIF_ALL_TAGS = ['_exif_ifd_pointer', '_gps_ifd_pointer', 'aperture_value', 'brightness_value', 'color_space',
 'components_configuration', 'compression', 'datetime', 'datetime_digitized', 'datetime_original', 'exif_version',
 'exposure_bias_value', 'exposure_mode', 'exposure_program', 'exposure_time', 'f_number', 'flash',
 'flashpix_version', 'focal_length', 'focal_length_in_35mm_film', 'gps_altitude', 'gps_altitude_ref',
 'gps_datestamp', 'gps_dest_bearing', 'gps_dest_bearing_ref', 'gps_horizontal_positioning_error',
 'gps_img_direction', 'gps_img_direction_ref', 'gps_latitude', 'gps_latitude_ref', 'gps_longitude',
 'gps_longitude_ref', 'gps_speed', 'gps_speed_ref', 'gps_timestamp', 'jpeg_interchange_format',
 'jpeg_interchange_format_length', 'lens_make', 'lens_model', 'lens_specification', 'make', 'maker_note',
 'metering_mode', 'model', 'orientation', 'photographic_sensitivity', 'pixel_x_dimension', 'pixel_y_dimension',
 'resolution_unit', 'scene_capture_type', 'scene_type', 'sensing_method', 'shutter_speed_value', 'software',
 'subject_area', 'subsec_time_digitized', 'subsec_time_original', 'white_balance', 'x_resolution',
 'y_and_c_positioning', 'y_resolution']


# iterate over files in that directory
def read_path(images):
    for filename in os.listdir(directory):
        full_path = os.path.join(directory, filename)

        # Skip directories
        if os.path.isdir(full_path):
            print(f"Skipping directory: {full_path}")
            continue

        # Remove .DS_Store
        if filename == ".DS_Store":
            try:
                os.remove(full_path)
                print(".DS_Store removed.")
            except Exception as e:
                print(f"Error removing .DS_Store: {e}")
            continue

        # Check for video files
        if ".mp4" in filename:
            print('\033[91m' + f"MP4 file found: {full_path}" + '\033[0m')
        elif ".mov" in filename:
            print('\033[91m' + f"MOV file found: {full_path}" + '\033[0m')
        else:
            # Add image files to the list
            images.append(filename)
    images.sort()




def find_coordinateds():
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    # calling the Nominatim tool and create Nominatim class
    geolocator = geopy.Nominatim(user_agent="images_editor")

    # entering the location name
    location = geolocator.geocode(city)

    # printing address
    print(location.address)
    lat = location.latitude
    lon = location.longitude
    url = f"https://api.opentopodata.org/v1/aster30m?locations={lat},{lon}"
    r = requests.get(url)
    data = r.json()
    alt = data['results'][0]['elevation']
    # printing latitude and longitude
    print(lat, lon, alt)
    return lat, lon, alt


# change date
def change_tags(images, lat, lon, alt):
    increment2 = 0
    changed = False
    for img in images:
        image_path = os.path.join(directory, img)
        with open(image_path, "rb") as input_file:
            exif_img = ExifImage(input_file)

        if(new_year and new_month and new_day):
            old_date = datetime(1970, 1, 1)
            try:
                old_date = datetime.strptime(exif_img.get("datetime_original"), "%Y:%m:%d %H:%M:%S")
            except:
                print("date in a wrong format")
                old_date = datetime(1970, 1, 1, 0, 0, 0)

            if (new_year): old_date = old_date.replace(year=new_year)
            if (new_month): old_date = old_date.replace(month=new_month)
            if (new_day): old_date = old_date.replace(day=new_day)

            if (new_hour): old_date = old_date.replace(hour=new_hour)
            if (new_minute): old_date = old_date.replace(minute=new_minute)
            if (new_second): old_date = old_date.replace(second=new_second)

            if (increment):
                old_date = old_date + timedelta(seconds=increment2)
                increment2 += increment

            # old_date = datetime(2020, 1, 1, 0, 0, 0)
            exif_img.datetime = old_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_img.datetime_digitized = old_date.strftime("%Y:%m:%d %H:%M:%S")
            exif_img.datetime_original = old_date.strftime("%Y:%m:%d %H:%M:%S")
            changed = True

        if(city):
            exif_img.gps_latitude = lat
            exif_img.gps_longitude = lon
            exif_img.gps_altitude = alt
            changed = True

        if(changed):
            with open(image_path, "wb") as ofile:
                ofile.write(exif_img.get_file())


# View data
def view_data(images):
    for img_filename in images:
        print(img_filename)
        image_path = os.path.join(directory, img_filename)

        # Check if the path is a file (not a directory)
        if os.path.isfile(image_path):
            with open(image_path, "rb") as input_file:
                exif_img = ExifImage(input_file)

            # Check if required EXIF tags are present
            try:
                if all(tag in exif_img and exif_img[tag] is not None for tag in EXIF_TAGS):
                    for tag in EXIF_TAGS:
                        value = exif_img[tag]
                        print("{}: {}".format(tag, value))
                else:
                    print("Required EXIF tags not present in {}".format(image_path))
            except KeyError as e:
                print("Error accessing EXIF data in {}: {}".format(image_path, e))
            except TypeError as e:
                print("Error accessing EXIF data in {}: {}".format(image_path, e))

            print("")
        else:
            print("{} is a directory, skipping.".format(image_path))


# View data
def view_first_all_data(img):
        print(img)
        image_path = os.path.join(directory, img)
        with open(image_path, "rb") as input_file:
            img = ExifImage(input_file)

        for tag in EXIF_ALL_TAGS:
            value = img.get(tag)
            if(value is not None):
                print("{}: {}".format(tag, value))


# View data
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

    view_data(images)
    #view_all_dates(images)
    #view_first_all_data(images[0])

    lat, lon, alt = 0, 0, 0
    if(city):
        print("\n")
        lat, lon, alt = find_coordinateds()

    areyousure = input("\nyou are changing the date to \033[93m" +str(new_day)+"/"+str(new_month)+"/"+str(new_year)+ "\033[0m are you sure? y/n:\n")
    if(areyousure == "y"):
        change_tags(images, lat, lon, alt)
        print("\nAFTER\n")
        view_data(images)
