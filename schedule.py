from together import Together
import json
import datetime
from dateutil.parser import parse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'path for credentials.json'
TOKEN_FILE = 'path for token.pickle'
TOGETHER_API_KEY="your_togetherai_api_key"
client = Together()

def authenticate_google_calendar():
    """Authenticate with Google Calendar API using OAuth 2.0."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def parse_event_details_with_llm(text):
    prompt = f"""
    You are a scheduling assistant. Parse the following input to extract event details: title (summary), date (YYYY-MM-DD), time (HH:MM in 24-hour format), and location.
    Return the details in JSON format with fields: summary, date, time, location.
    If any detail is missing or unclear, set it to null.
    Interpret dates and times in the 'Asia/Kolkata' timezone (IST, UTC+5:30).
    Input: "{text}"
    Example output: {{"summary": "Team meeting", "date": "2025-06-02", "time": "10:00", "location": "Zoom"}}
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.6
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3].strip()
        event_details = json.loads(content)
        if not event_details.get("summary") or not event_details.get("date"):
            raise ValueError("Missing required fields: summary or date")
        return event_details
    except (Exception, json.JSONDecodeError, ValueError) as e:
        print(f"LLM parsing error: {e}. Falling back to basic parsing.")
        event = {"summary": text.split()[0] if text.split() else None, "date": None, "time": None, "location": None}
        try:
            parsed_date = parse(text, fuzzy=True)
            event["date"] = parsed_date.date().isoformat()
            if parsed_date.time() != datetime.time(0, 0):
                event["time"] = parsed_date.time().strftime("%H:%M")
            words = text.lower().split()
            for i, word in enumerate(words):
                if word in ["in", "at"] and i + 1 < len(words):
                    event["location"] = " ".join(text.split()[i + 1:])
                    break
        except ValueError:
            pass
        return event

def confirm_event_details(event):
    print("\nExtracted Event Details:")
    print(f"Title: {event['summary'] or 'Not specified'}")
    print(f"Date: {event['date'] or 'Not specified'}")
    print(f"Time: {event['time'] or 'Not specified'}")
    print(f"Location: {event['location'] or 'Not specified'}")
    
    while True:
        confirm = input("\nAre these details correct? (yes/no): ").lower()
        if confirm in ["yes", "no"]:
            break
        print("Please enter 'yes' or 'no'.")
    
    if confirm == "no":
        event["summary"] = input("Enter event title (or press Enter to keep unchanged): ") or event["summary"]
        event["date"] = input("Enter date (YYYY-MM-DD, or press Enter to keep unchanged): ") or event["date"]
        event["time"] = input("Enter time (HH:MM, or press Enter to keep unchanged): ") or event["time"]
        event["location"] = input("Enter location (or press Enter to keep unchanged): ") or event["location"]
    return event

def create_google_calendar_event(service, event_details):
    start_time = event_details["time"] or "09:00"
    if not event_details["date"]:
        print("Error: Date is required to create an event.")
        return None
    
    try:
        start_datetime = f"{event_details['date']}T{start_time}:00+05:30"
        start_dt = datetime.datetime.fromisoformat(start_datetime)
        end_dt = start_dt + datetime.timedelta(hours=1)
        end_datetime = end_dt.isoformat()
    except ValueError as e:
        print(f"Error: Invalid date or time format: {e}")
        return None
    
    event = {
        "summary": event_details["summary"] or "Untitled Event",
        "location": event_details["location"] or "",
        "start": {
            "dateTime": start_datetime,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": "Asia/Kolkata"
        }
    }
    
    try:
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event_result.get('htmlLink')}")
        return event_result
    except Exception as e:
        print(f"Error creating event: {e}")
        return None

def main():
    if not os.getenv("TOGETHER_API_KEY"):
        print("Error: Please set the TOGETHER_API_KEY environment variable.")
        return
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: {CREDENTIALS_FILE} not found. Please download it from Google Cloud Console.")
        return
    
    print("Welcome to the Scheduling Assistant")
    service = authenticate_google_calendar()
    
    while True:
        user_input = input("\nEnter event details :")
        if user_input.lower() == 'exit':
            break
        
        # Parse input with Together AI
        event_details = parse_event_details_with_llm(user_input)
        
        # Check if critical details are missing
        if not event_details["summary"] or not event_details["date"]:
            print("Could not extract sufficient event details. Please provide at least an event title and date.")
            continue
        
        # Confirm details with user
        event_details = confirm_event_details(event_details)
        
        # Create event in Google Calendar
        create_google_calendar_event(service, event_details)

if __name__ == "__main__":
    main()