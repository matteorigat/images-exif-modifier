import os
#import sys
#import filedate
from datetime import datetime, timedelta
# pip3 install exif
from exif import Image as ExifImage

# assign directory
directory = '/Volumes/SanDisk/Matteo/Foto Matteo completo/2005-04 Venezia'

# new date  -> if False the old value will remain
new_year = 2015  # like 2023 or False
new_month = 5  # max 12 or False
new_day = 15  # max 31 or False

new_hour = False  # max 23 or False
new_minute = False  # max 59 or False
new_second = False  # max 59 or False

# do you want to increment photos timestamps
# to have them in the order in which they are read
# recommended only if you set also the time
increment = 1  # in seconds of False



changecoord = False

"""

DO NOT EDIT BELOW !!!

"""

EXIF_TAGS = [
     "make",
     "model",
     "datetime",
     "datetime_digitized",
     "datetime_original",
     "gps_latitude",
     "gps_latitude_ref",
     "gps_longitude",
     "gps_longitude_ref",
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




# change date
def change_date(images):
    increment2 = 0
    for img in images:
        image_path = os.path.join(directory, img)
        with open(image_path, "rb") as input_file:
            exif_img = ExifImage(input_file)

        old_date = datetime(1970, 1, 1)
        try:
            old_date = datetime.strptime(exif_img.get("datetime_original"), "%Y:%m:%d %H:%M:%S")
        except:
            print("date in a wrong format")

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


        if(changecoord):
            exif_img.gps_latitude
            exif_img.gps_longitude
            exif_img.gps_altitude


        with open(image_path, "wb") as ofile:
            ofile.write(exif_img.get_file())


# View data
def view_data(images):
    for img in images:
        print(img)
        image_path = os.path.join(directory, img)
        with open(image_path, "rb") as input_file:
            img = ExifImage(input_file)

        for tag in EXIF_TAGS:
            value = img.get(tag)
            print("{}: {}".format(tag, value))

        print("")


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


def view_all_dates(images):
    for img in images:
        print(img)
        image_path = os.path.join(directory, img)
        with open(image_path, "rb") as input_file:
            img = ExifImage(input_file)

        print("{}: {}".format("datetime_original", img.get("datetime_original")))






# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    images = []

    # iterate over files in that directory
    for filename in os.listdir(directory):
        if(filename==".DS_Store"):
            try:
                os.remove(os.path.join(directory, filename))
            except:
                print("Errore remove .DS_Store manually")

        images.append(filename)

    view_all_dates(images)

    #view_first_all_data(images[0])

    #change_date(images)

    #print("\nAFTER\n")
    #view_data(images)


















""" # checking if it is a file
    if os.path.isfile(a):
        with open(a, 'rb') as image_file:
            my_image = Image(image_file)
            my_image.model = "Pixel 10"
            print(my_image.get("datetime_original"), my_image.get("gps_longitude"), my_image.get("model"))
            #sys.exit()





        a_file = filedate.File(a)

        a_file.set(
            created = "2022.01.01 13:00:00",
            modified = "2022.01.01 13:00:00",
            accessed = "2022.01.01 13:00:00"
        )

        #after = filedate.File(a)
        #print(after.get())"""