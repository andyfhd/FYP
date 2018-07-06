# python modules to install from pip: simplejson
# 1. to install shapely for Windows, go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
# 2. pip install wheel
# 3. pip install <wheel-file-downloaded>

data_folder = "Datasets_for_analysis/"
combine_folder = "Combine/"
combine_file = "combine.csv"
enrich_file = "combine_with_location.csv"

place_list_path = "placelists_from_SUTD/finalPlaceList.json"    # need to wrap raw file with []
cluster_list_path = "placelists_from_SUTD/clusterList.json"  # need to wrap raw file with []
finalPlaceList = []  # POI list
clusterList = []  # cluster list

import simplejson as json
from shapely.geometry import shape, Point
from shapely.geometry.polygon import Polygon
from shapely import geometry

# load locations into memory
json_data = open(data_folder + place_list_path).read()
finalPlaceList = json.loads(json_data)

for geo_list in finalPlaceList:
    polygon = geometry.Polygon(geo_list['geometry']['coordinates'][0])
    geo_list['polygon'] = polygon

json_data = open(data_folder + cluster_list_path).read()
clusterList = json.loads(json_data)

for geo_list in clusterList:
    polygon = geometry.Polygon(geo_list['geometry']['coordinates'][0])
    geo_list['polygon'] = polygon


import csv
import traceback
import os
try:
    enrich_cache = []
    with open(combine_folder + combine_file, 'r') as combine_csv:
        row_count = sum(1 for row in combine_csv)
        print("total records: " + str(row_count))

    with open(combine_folder + combine_file, 'r') as combine_csv:

        combine_reader = csv.reader(combine_csv, delimiter=',')

        for row in combine_reader:

            hit_regions = []
            for geo_list in finalPlaceList:
                if geo_list['polygon'].contains(Point(float(row[5]), float(row[6]))):
                    hit_regions.append(geo_list)

            if len(hit_regions) == 0:
                place_name = "U"
                category = "U"
                parent_category = "U"
            else:   # TODO: when multiple regions are hit, find the closest
                place_name = hit_regions[0]["properties"]["placeName"]
                category = hit_regions[0]["properties"]["category"]
                parent_category = hit_regions[0]["properties"]["parentCategory"]

            hit_clusters = []
            for geo_list in clusterList:
                if geo_list['polygon'].contains(Point(float(row[5]), float(row[6]))):
                    hit_clusters.append(geo_list)

            if len(hit_clusters) == 0:
                cluster_id = "U"
                cluster_name = "U"
                radius = 0
            else:   # TODO: when multiple clusters are hit, find the closest
                cluster_id = hit_clusters[0]["properties"]["clusterID"]
                cluster_name = hit_clusters[0]["properties"]["clusterName"]
                radius = hit_clusters[0]["properties"]["radius"]

            enrich_cache.append(row + [place_name, category, parent_category, cluster_id, cluster_name, radius])

            if len(enrich_cache) % 10000 == 0:
                print(str(len(enrich_cache)) + " out of " + str(row_count) + " processed")

    with open(combine_folder + enrich_file, 'w') as enrich_csv:
        enrich_writer = csv.writer(enrich_csv, delimiter=',', lineterminator="\n")
        enrich_writer.writerow(['userid', 'gender', 'age group', 'app version', 'family ID', 'family size', 'date', 'time',
                                'longitude', 'latitude', 'weight', 'type I frequency', 'type II frequency', 'type II frequency',
                                'old place name', 'old category', 'old parent category', 'cluster ID', 'cluster name', 'radius'])
        for row in enrich_cache:
            enrich_writer.writerow(row)
except Exception as err:
    print(err)
    traceback.print_tb(err.__traceback__)
