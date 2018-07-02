data_folder = "Data/"
output_folder = "Output/"

loc_folders = ["passive_data_loc_05may2017", "passive_data_loc_6jun2017"]
act_folders = ["processed_activity_05may2017", "processed_activity_6jun2017"]
loc_raw_files = {}  # folder->list of location files
act_raw_files = {}  # folder->list of activity files

import os
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
for loc_folder in loc_folders:
    loc_raw_files[loc_folder] = [f for f in os.listdir(data_folder + loc_folder) if os.path.isfile(os.path.join(data_folder + loc_folder, f))]
for act_folder in act_folders:
    act_raw_files[act_folder] = [f for f in os.listdir(data_folder + act_folder) if os.path.isfile(os.path.join(data_folder + act_folder, f))]


def get_user_activities(user):
    activities = {}
    for activity_folder in act_raw_files:    # load user activities
        activity_files = [t for t in act_raw_files[activity_folder] if t.startswith(user)]

        if len(activity_files) > 0:
            for activity_filename in activity_files:
                activity_date = activity_filename.split(".")[0].split("_")[1]
                with open(data_folder + activity_folder + "/" + activity_filename, 'r') as activity_csv:
                    activity_reader = csv.reader(activity_csv, delimiter=',')

                    for activity_row in activity_reader:    # 0.date  1.time  2.activity
                        if activity_date not in activities:
                            activities[activity_date] = []

                        activities[activity_date].append([activity_row[0], activity_row[1]])

    return activities


import csv
import traceback
try:
    with open(data_folder + 'User_Demographics_20180522.csv', 'r') as user_csv:
        user_reader = csv.reader(user_csv, delimiter=',')

        next(user_reader)

        for user_row in user_reader:    # main user loop
            user = user_row[0]
            print("processing user " + user)
            gender = user_row[1]
            age_group = user_row[2]

            user_activities = get_user_activities(user)

            with open(output_folder + user + "_loc.csv", 'w') as output_csv:
                output_writer = csv.writer(output_csv, delimiter=',', lineterminator="\n")
                output_cache = []

                for location_folder in loc_raw_files:    # input location file loop
                    location_files = [t for t in loc_raw_files[location_folder] if t.startswith(user)]
                    if len(location_files) > 0:
                        with open(data_folder + location_folder + "/" + location_files[0], 'r') as location_csv:
                            location_reader = csv.reader(location_csv, delimiter='\t')

                            for location_row in location_reader:  # input location row loop
                                # 0.userid  1.gender  2.age group  3.date  4.time  5.longitude  6.latitude
                                output_cache.append([location_row[0], gender, age_group, location_row[1], location_row[2], location_row[5], location_row[6]])

                if len(output_cache) > 0:
                    output_cache.sort(key=lambda x: (x[3], x[4]))

                    previous_row = []
                    for output_row in output_cache:
                        if len(previous_row) == 0 or output_row[3] != previous_row[3]:    # ignore first record for each new day
                            previous_row = output_row
                            continue
                        day_activities = user_activities[output_row[3]] if output_row[3] in user_activities else []
                        current_activities = [t for t in day_activities if t[0] > previous_row[4] and t[0] < output_row[4]]
                        if len(current_activities) > 0:
                            from itertools import groupby
                            act_breakdown = {'1': 0, '2': 0, '3': 0}
                            for key, group in groupby(current_activities, key=lambda x: x[1]):
                                act_breakdown[key] = len(list(group))/len(current_activities)

                            # 7.weight  8.type I frequency  9.type II frequency  10.type III frequency
                            output_writer.writerow(output_row + [len(current_activities), act_breakdown['1'], act_breakdown['2'], act_breakdown['3']])
                        previous_row = output_row
except Exception as err:
    print(err)
    traceback.print_tb(err.__traceback__)
