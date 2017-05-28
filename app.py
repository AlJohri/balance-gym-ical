import os
import arrow
import requests
from io import BytesIO
from icalendar import Calendar, Event
from flask import Flask, send_file

app = Flask(__name__)

SCHEDULE_API = "https://balancegym.mosomyclub.com/api/1.0/calendarevents/eventspan/"

def date_to_ical_date(date):
    return date.format('YYYYMMDD') + 'T' + date.format('HHmmss') + 'Z'

def parse(event):

    try:
        instructor = [resource for resource in event['Resources'] if resource['ResourceType'] == 'Employee'][0]['ResourceName']
    except IndexError:
        instructor = None

    try:
        room = [resource for resource in event['Resources'] if resource['ResourceType'] == 'Resource'][0]['ResourceName']
    except IndexError:
        room = None

    return {
        "id": event['EventOccurrenceId'],
        "category": event['EventCategoryName'], # EventCategoryId
        "start_date": arrow.get(event['StartDateUTC'], "M/D/YYYY h:mm A", tzinfo='utc'),
        "end_date": arrow.get(event['EndDateUTC'], "M/D/YYYY h:mm A", tzinfo='utc'),
        "name": event['Name'],
        "room": room,
        "instructor": instructor
    }

def get_events(location_id, date):
    events = []
    params = {"businessUnitId": location_id, "targetDate": date, "span": "week"}
    response = requests.get(SCHEDULE_API, params=params)
    data = response.json()
    for day, day_events in data['Result']['Data']['CalendarEventDatesResult']['EventDates'].items():
        events += day_events
    return events

@app.route("/<location>.ics")
def schedule(location):

    if location == "thomas-circle":
        location_id = 1
    else:
        raise Exception(f"location {location} is unknown")

    today = arrow.now().strftime("%x")
    next_week = arrow.now().replace(weeks=1).strftime("%x")
    events = [parse(event) for date in [today, next_week] for event in get_events(location_id, date)]

    cal = Calendar()
    for event in events:
        cal_event = Event()
        cal_event['uid'] = event['id']
        cal_event['dtstart'] = date_to_ical_date(event['start_date'])
        cal_event['dtend'] = date_to_ical_date(event['end_date'])
        cal_event['summary'] = event['name']
        cal_event['location'] = event['room']
        cal.add_component(cal_event)

    return send_file(BytesIO(cal.to_ical()),
        attachment_filename='thomas-circle.ics',
        mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
