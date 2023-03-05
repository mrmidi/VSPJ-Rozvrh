# vspjcal - create ics file from vspj timetable
# (c) 2023 by Aleksandr Shabelnikov
import os
import sys
import vspjcal

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

# # enter start date
# start_date = input("Enter start date (dd.mm.YYYY): ")
#
# # enter end date
# end_date = input("Enter end date (dd.mm.YYYY): ")

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

vspjcal.process_file(filename)