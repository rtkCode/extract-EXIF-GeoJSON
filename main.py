import os
import json
from datetime import datetime
import exifread

GEOJSON_LIST = []

STATUS = {
    "success": 0,
    "fail": 0
}

def run():
    photos_path = "photos"
    photos = os.listdir(photos_path)
    for photo in photos:
        # escape hidden files
        if photo[0] == ".":
            continue
        # open files
        p = open(photos_path + "/" + photo, 'rb')
        try:
            date_location = get_date_location(p)
            GEOJSON_LIST.append(geojson_template(date_location))
            STATUS["success"] += 1
        except:
            STATUS["fail"] += 1
    write_results()

def get_date_location(file):
    exif_dict = exifread.process_file(file)

    exif_datetime = exif_dict['EXIF DateTimeOriginal'].printable
    export_datetime = str(datetime.strptime(exif_datetime, '%Y:%m:%d %H:%M:%S'))

    lon_ref = exif_dict["GPS GPSLongitudeRef"].printable
    lon = exif_dict["GPS GPSLongitude"].printable
    lat_ref = exif_dict["GPS GPSLatitudeRef"].printable
    lat = exif_dict["GPS GPSLatitude"].printable

    location = convert_location(lon_ref, lon, lat_ref, lat)

    return {
        "datetime": export_datetime,
        "location": location
    }

def convert_location(lon_ref, longitude, lat_ref, latitude):
    # Longitude
    lon = longitude[1:-1].replace(" ", "").replace("/", ",").split(",")
    lon = float(lon[0]) + float(lon[1]) / 60 + float(lon[2]) / float(lon[3]) / 3600
    if lon_ref != "E":
        lon = lon * (-1)

    # Latitude
    lat = latitude[1:-1].replace(" ", "").replace("/", ",").split(",")
    lat = float(lat[0]) + float(lat[1]) / 60 + float(lat[2]) / float(lat[3]) / 3600
    if lat_ref != "N":
        lat = lat * (-1)

    # return [lat, lon, 20]
    return [lat, lon]

def geojson_template(date_location):
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": date_location["location"]
        },
        "properties": {
            "datetime": date_location["datetime"],
        },
        
    }

def write_results():
    # print(GEOJSON_LIST)
    print("Successfully extracted {} locations, {} failed".format(STATUS["success"], STATUS["fail"]))
    file = open("Geo.json", "w")
    file.write(json.dumps(GEOJSON_LIST, sort_keys=True, indent=4, separators=(', ', ': ')))

run()
