# scrap VSPJ schedule from IS

# beautiful soup
from bs4 import BeautifulSoup
# import time
import datetime


from ics import Calendar, Event

c = Calendar()

# global variable start_date (d, m, y)
start_date = datetime.datetime(2023, 3, 6) # 6.3.2023

class Subject:
    def __init__(self, day, start_time, end_time, subject_type, subject, teacher, room, title):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.subject_type = subject_type
        self.subject = subject
        self.teacher = teacher
        self.room = room
        self.title = title

    def __str__(self):
        return f"{self.day} {self.start_time} {self.end_time} {self.subject_type} {self.subject} {self.teacher} {self.room} {self.title}"


    # TIME TABLE
    # 0 - 7:10 - 7:55
    # 1 - 8:00 - 8:45
    # 2 - 8:50 - 9:35
    # 3 - 9:45 - 10:30
    # 4 - 10:35 - 11:20
    # 5 - 11:30 - 12:15
    # 6 - 12:35 - 13:20
    # 7 - 13:30 - 14:15
    # 8 - 14:20 - 15:05
    # 9 - 15:15 - 16:00
    # 10 - 16:05 - 16:50
    # 11 - 17:00 - 17:45
    # 12 - 17:50 - 18:35
    # 13 - 18:45 - 19:30

def get_time(hour, length=1):
    start_time = {
        0: "7:10",
        1: "8:00",
        2: "8:50",
        3: "9:45",
        4: "10:35",
        5: "11:30",
        6: "12:35",
        7: "13:30",
        8: "14:20",
        9: "15:15",
        10: "16:05",
        11: "17:00",
        12: "17:50",
        13: "18:45"
    }
    end_time = {
        0: "7:55",
        1: "8:45",
        2: "9:35",
        3: "10:30",
        4: "11:20",
        5: "12:15",
        6: "13:20",
        7: "14:15",
        8: "15:05",
        9: "16:00",
        10: "16:50",
        11: "17:45",
        12: "18:35",
        13: "19:30",
        14: "20:15"
    }
    return start_time[hour], end_time[hour+length-1]

def get_day(day):
    days = {
        'po': 0,
        'út': 1,
        'st': 2,
        'čt': 3,
        'pá': 4,
        'so': 5,
        'ne': 6
    }

    return days[day]


schedule = []




def add_event(subject):
    begin_time, end_time = get_timeslot(subject)

    print("Preparing event...")
    print(f"Subject: {subject.subject}")
    print(f"Teacher: {subject.teacher}")
    print(f"Type: {subject.subject_type}")
    print(f"Title: {subject.title}")
    print(f"Location: {subject.room}")
    print(f"Begin: {begin_time}")
    print(f"End: {end_time}")
    print("")

    e = Event()
    e.name = subject.subject + " " + subject.subject_type
    e.description = subject.title
    e.location = subject.room
    e.begin = begin_time
    e.end = end_time
    e.organizer = subject.teacher

    # repeat every week

    # end repeat on 01.06.2023
    # color of event



    c.events.add(e)

    # e = Event()
    # e.name = subject.subject
    # e.description = subject.title
    # e.location = subject.room
    #
    # e.begin = datetime.datetime(2021, 9, 1, 7, 10)
    # e.end = datetime.datetime(2021, 9, 1, 7, 55)
    # c.events.add(e)

def make_calendar():
    for subject in schedule:
        add_event(subject)

def get_timeslot(subject):
    # is start date monday?
    if start_date.weekday() == 0:
        monday_date = start_date
    else:
        monday_date = start_date - datetime.timedelta(days=start_date.weekday())
    start_time = subject.start_time
    end_time = subject.end_time
    date = monday_date + datetime.timedelta(days=subject.day)

    start_time = datetime.datetime.strptime(start_time, '%H:%M').time()
    end_time = datetime.datetime.strptime(end_time, '%H:%M').time()
    #start_time = datetime.time.strftime('%H:%M:%S', datetime.datetime.strptime(start_time, '%H:%M').time())
    begin_date = datetime.datetime.combine(date, start_time)
    end_date = datetime.datetime.combine(date, end_time)
    return begin_date, end_date



def process_row(cells, day):

    hour = 0
    for cell in cells:
        if cell.has_attr('colspan'):
            length = int(cell['colspan'])
        else:
            length = 1
        # beautiful soup: get <abbr> tag
        abbr = cell.find('abbr')
        if abbr is not None:
            # get text between <abbr> and </abbr>
            subject = abbr.get_text()
            # trim the text
            subject = subject.strip()
            # prednaska or cviceni
            # find text ". př" or ". cv"
            small_text = cell.find('small').text.strip()
            # get teacher
            splitted = small_text.split(" ")

            splitted = [x.strip() for x in splitted]
            splitted = list(filter(None, splitted))
            print("splitted: " + str(splitted))

            if splitted[1] == "př":
                subject_type = "Přednáška"
            elif splitted[1] == "cvi":
                subject_type = "Cvičení"

            room = splitted[2]
            teacher = splitted[-2]
            title = abbr['title']



            print("room: " + room)
            print("teacher: " + teacher)
            print("Subject type: " + subject_type)
            print ("subject: " + subject)
            print("title:" + abbr['title'])
            print("length: " + str(length))
            print("hour: " + str(hour))
            print(f"start time: {get_time(hour)}")

            s = Subject(get_day(day), get_time(hour, length)[0], get_time(hour, length)[1], subject_type, subject,
                        teacher, room, title)

            schedule.append(s)
            hour = hour + length


        else:
            hour = hour + length


def print_schedule():
    for subject in schedule:
        print(subject)


def process_file(filename):
    rowspans = []
    days = []
    file = open(filename, 'r')
    soup = BeautifulSoup(file, 'html.parser')
    # get all the rows
    rows = soup.find_all('tr')
    # get all <th> tags
    headers = soup.find_all('th')
    #count headers with 2 letters in the <th> tag
    count = 0
    for header in headers:
        if len(header.text) == 2:
            rowspan = int(header['rowspan'])
            for i in range(rowspan):
                days.append(header.text)
            count = count + 1
    i = 1
    for day in days:
        row = rows[i]
        cells = row.find_all('td')
        process_row(cells, day)
        i = i + 1

    print("done")
    print_schedule()
    make_calendar()

    print(c)

    with open('calendar.ics', 'w') as f:
        f.writelines(c.serialize_iter())

    f.close()


