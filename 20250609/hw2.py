import glob
import os
import csv

def merge_all_bus_info_csv():
    input_folder = "data/BUS_INFO"
    output_file = "data/merged_bus_info.csv"
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    header_saved = False

    with open(output_file, "w", newline="", encoding="utf-8") as fout:
        writer = None
        for file in csv_files:
            with open(file, "r", encoding="utf-8") as fin:
                reader = csv.reader(fin)
                header = next(reader)
                if not header_saved:
                    writer = csv.writer(fout)
                    writer.writerow(header)
                    header_saved = True
                for row in reader:
                    writer.writerow(row)
    print(f"所有CSV已合併到 {output_file}")

# 使用方式：呼叫 merge_all_bus_info_csv()
merge_all_bus_info_csv()