import datetime
import os.path
from pprint import pprint
from uuid import uuid4
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]
creds = Credentials.from_authorized_user_file("token.json", SCOPES)

def main():
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return

    # Prints the start and name of the next 10 events
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])






event = {
  'summary': 'Test',
  "anyoneCanAddSelf": True,
  'location': 'google meeting room',
  'description': 'A chance to hear more about Google\'s developer products.',
  'start': {
    'dateTime': (datetime.datetime.now() + datetime.timedelta(5)).isoformat() + "Z",
    'timeZone': 'UTC+3',
  },
  'end': {
    'dateTime': (datetime.datetime.now() + datetime.timedelta(5, seconds=60 * 5)).isoformat() + "Z",
    'timeZone': 'UTC+3',
  },
  'recurrence': [
    'RRULE:FREQ=DAILY;COUNT=2'
  ],
  'attendees': [
    {'email': 'atajceces@gmail.com'
     },
  ],
  'reminders': {
    'useDefault': "atajceces@gmail.com",
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
    "conferenceData":
        {"conferenceDataVersion": 1,
         "createRequest":{
            "requestId": f"{uuid4().hex}",
             "conferenceSolutionKey": {
                 "type": "hangoutsMeet",
                }},
  }
}

service = build("calendar", "v3", credentials=creds)
event = service.events().insert(calendarId="primary", sendNotifications=True, body=event, conferenceDataVersion=1).execute()
rsp = service.events().update
print('Event created: %s' % (event))
pprint(event)
rule = {
    'scope': {
        'type': 'user',
        'value': 'atajceces@gmail.com',
    },
    'role': 'owner'
}

created_rule = service.acl().insert(etag="3469083023418000", body=rule).execute()

pprint(created_rule)
