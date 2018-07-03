from flask import Flask, request, Response, url_for
from twilio.twiml.voice_response import VoiceResponse
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def forward_call():
    """Forward incoming phone calls to the certain number."""
    forward_to = '+' + request.values.get('forward_to')
    response = VoiceResponse()
    response.dial(forward_to,
                  action=url_for('log_to_googlesheet',
                                 forward_to=forward_to,
                                 spread_sheet=request.values.get('sheet')))
    return Response(str(response), 200, mimetype="application/xml")

@app.route("/googlesheet/<forward_to>/<spread_sheet>", methods=['GET', 'POST'])
def log_to_googlesheet(forward_to, spread_sheet):
    """Write row to Google Spreadsheet about call"""
    row = [
        int(datetime.datetime.now().timestamp()),
        request.values.get('From'),
        forward_to
    ]
    client = get_auth()
    sheet = client.open(spread_sheet).sheet1
    sheet.append_row(row)
    return Response(
        str('Record added to the Google Spreadsheet'),
        200, mimetype="application/xml")


def get_auth():
    """Authorization for the Google Drive API"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'client_secret.json', scope)
    client = gspread.authorize(credentials)
    return client


if __name__ == "__main__":
    app.run(debug=False)
