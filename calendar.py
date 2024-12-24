import datetime
import datetime
import os.path

from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
creds = Credentials.from_authorized_user_file('tets_toke.json', SCOPES)

