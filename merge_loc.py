data_folder = "Data/"
loc_folders = ["passive_data_loc_05may2017", "passive_data_loc_6jun2017"]
loc_raw_files = {}

from os import listdir
from os.path import isfile, join
for loc_folder in loc_folders:
    loc_raw_files[loc_folder] = [f for f in listdir(
        data_folder + loc_folder) if isfile(join(data_folder + loc_folder, f))]


import csv
with open(data_folder + 'User_Demographics_20180522.csv', 'r') as user_csv:
    user_reader = csv.reader(user_csv, delimiter=',')

    next(user_reader)

    for user_row in user_reader:    # main user loop
        user = user_row[0]
        gender = user_row[1]
        age_group = user_row[2]

        with open("Output/" + user + "_loc.csv", 'w') as output_csv:
            output_writer = csv.writer(output_csv, delimiter=',')
            output_cache = []

            for folder in loc_raw_files:    # input file loop
                result = [t for t in loc_raw_files[folder]
                          if t.startswith(user + ".txt")]
                if len(result) > 0:
                    with open(data_folder + folder + "/" + result[0], 'r') as input_csv:
                        input_reader = csv.reader(input_csv, delimiter='\t')

                        for input_row in input_reader:  # input row loop
                            output_cache.append(
                                [input_row[0], gender, age_group, input_row[1] + "T" + input_row[2], input_row[5], input_row[6]])

            if len(output_cache) > 0:   # sort and write output
                output_cache.sort(key=lambda x: x[3])

                for output_row in output_cache:
                    output_writer.writerow(output_row)
