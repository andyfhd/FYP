output_folder = "Output/"
combine_folder = "Combine/"
combine_file = "combine.csv"

import csv
import traceback
import os
try:
    if not os.path.exists(combine_folder):
        os.makedirs(combine_folder)

    combine_cache = []
    for f in os.listdir(output_folder):
        with open(output_folder + f, 'r') as output_csv:
            output_reader = csv.reader(output_csv, delimiter=',')

            for row in output_reader:
                combine_cache.append(row)

    combine_cache.sort(key=lambda x: (x[6], x[7]))

    with open(combine_folder + combine_file, 'w') as combine_csv:
        output_writer = csv.writer(combine_csv, delimiter=',', lineterminator="\n")
        for row in combine_cache:
            output_writer.writerow(row)
except Exception as err:
    print(err)
    traceback.print_tb(err.__traceback__)
