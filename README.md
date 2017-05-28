# balance-gym-ical

## iCal Links

- https://balance-gym-ical.herokuapp.com/thomas-circle.ics
- https://balance-gym-ical.herokuapp.com/glover-park.ics
- https://balance-gym-ical.herokuapp.com/foggy-bottom.ics
- https://balance-gym-ical.herokuapp.com/bethesda.ics
- https://balance-gym-ical.herokuapp.com/capitol-hill.ics

## Development

### Setup
```
mkvirtualenv -p python3 -r requirements.txt balance-gym-ical
```

### Usage
```
workon balance-gym-ical
python app.py
```

### Heroku
```
heroku apps:create balance-gym-ical # first time only
heroku git:remote --app corepower-yoga-ical
git push heroku master
```

## Source

- https://balancegym.mosomyclub.com/class-schedules.aspx