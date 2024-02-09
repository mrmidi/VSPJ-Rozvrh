# vspjcal - create ics file from vspj timetable
# (c) 2023 by Aleksandr Shabelnikov
import os
import sys
import vspjcal
import datetime

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))


# get today date in format DD.MM.YYYY
start_date_input = input("Enter start date (dd.mm.YYYY). Default is 06.03.2023: ")
if start_date_input == "":
    start_date_input = "06.03.2023"
# convert to datetime outside of the conditional block to ensure it's always applied
start_date = datetime.datetime.strptime(start_date_input, "%d.%m.%Y")


# # enter end date
end_date = input("Enter end date (dd.mm.YYYY): Default is 11.06.2023: ")
if end_date == "":
    end_date = "11.06.2023"
    time = "00:00:00"
    # convert to datetime
    end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y")
    end_date = datetime.datetime.combine(end_date, datetime.datetime.strptime(time, "%H:%M:%S").time())
    # convert to 20230310T103000Z format
    end_date = end_date.strftime("%Y%m%dT%H%M%SZ")

# find all html files in current directory
pwd = os.getcwd()
files = os.listdir(pwd)
html_files = [file for file in files if file.endswith(".html")]

if len(html_files) == 0:
    filename = input(f"Enter filename: ")
else:
    print("Found html files in current directory:")
    for index, file in enumerate(html_files):
        print(f"{index + 1}. {file}")
    choice = input(f"Enter filename (1-{len(html_files)}): ")
    if choice.isdigit():
        filename = html_files[int(choice) - 1]

print(f"filename: {filename}")

vspjcal.start_date = start_date
vspjcal.end_date = end_date
vspjcal.process_file(filename)