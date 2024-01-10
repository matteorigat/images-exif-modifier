import os
#import sys
#import filedate
from datetime import datetime, timedelta
# pip3 install exif
from exif import Image as ExifImage

# assign directory
directory = '/Users/matteorigat/Desktop/images_copy'

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

"""

DO NOT EDIT BELOW !!!

"""

EXIF_TAGS = [
    #"make",
    # "model",
    "datetime_original",
    # "gps_latitude",
    # "gps_latitude_ref",
    # "gps_longitude",
    # "gps_longitude_ref",
    # "gps_altitude",
]

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

        with open(img, "wb") as ofile:
            ofile.write(exif_img.get_file())

        break


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
        break




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    images = []

    # iterate over files in that directory
    for filename in os.listdir(directory):
        images.append(filename)

    print("\nFIRST LOOK\n")
    view_data(images)

    change_date(images)

    print("\nAFTER\n")
    view_data(images)


















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