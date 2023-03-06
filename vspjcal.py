# scrap VSPJ schedule from IS
import os

# beautiful soup
from bs4 import BeautifulSoup
import datetime

from ics import Calendar, Event, Organizer
from ics.grammar.parse import ContentLine

c = Calendar()
start_date = datetime.datetime(2023, 3, 6) # 6.3.2023
end_date = datetime.datetime(2023, 6, 11) # 11.6.2023

def set_start_date(date):
    global start_date
    # convert dd.mm.yyyy to datetime
    date = datetime.datetime.strptime(date, "%d.%m.%Y")
    start_date = datetime.datetime(date)


def set_end_date(date):
    global end_date
    # convert dd.mm.yyyy to datetime
    date = datetime.datetime.strptime(date, "%d.%m.%Y")
    end_date = datetime.datetime(date)


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
        return f"{self.day} {self.start_time} {self.end_time} {self.subject_type} {self.subject} {self.teacher} " \
               f"{self.room} {self.title}"


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

    rrule = f"FREQ=WEEKLY;UNTIL={end_date}"
    e = Event()
    # teacher = name + email
    # ORGANIZER;CN="Sally Example":mailto:sally@example.com
    organizer = Organizer(common_name=subject.teacher, email=teachers[subject.teacher])

    e.name = subject.subject + " " + subject.subject_type
    e.description = subject.title
    e.location = subject.room
    e.begin = begin_time
    e.end = end_time
    e.organizer = organizer
    e.extra.append(ContentLine(name="RRULE", value=rrule))

    c.events.add(e)
    print("Added event: " + subject.title + " (" + subject.subject_type + ")")


def make_calendar():
    print("Making calendar...")
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

    begin_date = datetime.datetime.combine(date, start_time)
    end_date = datetime.datetime.combine(date, end_time)

    # utc to cet
    begin_date = begin_date - datetime.timedelta(hours=1)
    end_date = end_date - datetime.timedelta(hours=1)
    return begin_date, end_date


teachers = {}

# if teachers.txt exists - import it
if os.path.isfile('teachers.txt'):
    print("Loading teachers.txt...")
    with open('teachers.txt') as f:
        for line in f:
            (key, val) = line.split()
            teachers[key] = val
else:
    print("teachers.txt not found")


# teachers dict: teacher -> email


def process_row(cells, day):

    hour = 0
    for cell in cells:
        if cell.has_attr('colspan'):  # count colspan. if colspan is 2, then it is 2 hours long
            length = int(cell['colspan'])
        else:
            length = 1
        abbr = cell.find('abbr')
        if abbr is not None:
            # get text between <abbr> and </abbr>
            subject = abbr.get_text()
            # trim the text
            subject = subject.strip()
            small_text = cell.find('small').text.strip()
            splitted = small_text.split(" ")
            splitted = [x.strip() for x in splitted]
            splitted = list(filter(None, splitted))

            if splitted[1] == "př":
                subject_type = "Přednáška"
            elif splitted[1] == "cvi":
                subject_type = "Cvičení"

            room = splitted[2]
            teacher = splitted[-2]
            if teacher not in teachers:
                teachers[teacher] = teacher + "@vspj.cz"
            title = abbr['title']

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

    # print_schedule()
    make_calendar()

    # if teachers.txt not exists, create it
    if not os.path.exists('teachers.txt'):
        print("Creating teachers.txt. Please modify their emails if you need to and re-run the program.")
        with open('teachers.txt', 'w') as f:
            for teacher in teachers:
                f.write(f"{teacher} {teachers[teacher]}\n")

    with open('calendar.ics', 'w') as f:
        f.writelines(c.serialize_iter())

    f.close()


