import os
import arrow
import requests
from io import BytesIO
from icalendar import Calendar, Event
from flask import Flask, send_file

app = Flask(__name__)

SCHEDULE_API = "https://balancegym.mosomyclub.com/api/1.0/calendarevents/eventspan/"

# https://balancegym.mosomyclub.com/api/1.0/calendarevents/locations
# https://balancegym.mosomyclub.com/api/1.0/calendarevents/categories
# https://balancegym.mosomyclub.com/api/1.0/calendarevents/eventspan?businessUnitId=1&targetDate=5/28/2017&span=week

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
    params = {"businessUnitId": location_id, "targetDate": date.strftime("%x"), "span": "week"}
    response = requests.get(SCHEDULE_API, params=params)
    data = response.json()
    for day, day_events in data['Result']['Data']['CalendarEventDatesResult']['EventDates'].items():
        events += day_events
    return events

@app.route("/<location>.ics")
def schedule(location):

    if location == 'thomas-circle':
        location_id = 1
    elif location == 'glover-park':
        location_id = 2
    elif location == 'foggy-bottom':
        location_id = 3
    elif location == 'bethesda':
        location_id = 4
    elif location == 'capitol-hill':
        location_id = 9
    else:
        return f"location {location} is unknown", 500

    today = arrow.get(arrow.utcnow().date())

    dates = [
        today,
        today.replace(weeks=1)
    ]

    events = [parse(event) for date in dates for event in get_events(location_id, date)]

    cal = Calendar()
    for event in events:
        cal_event = Event()
        cal_event['uid'] = event['id']
        cal_event['dtstart'] = date_to_ical_date(event['start_date'])
        cal_event['dtend'] = date_to_ical_date(event['end_date'])
        cal_event['summary'] = event['name']
        cal_event['description'] = event['instructor']
        cal_event['location'] = event['room']
        cal_event['categories'] = event['category']
        cal.add_component(cal_event)

    return send_file(BytesIO(cal.to_ical()),
        attachment_filename=f'{location}.ics',
        mimetype='text/calendar')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
