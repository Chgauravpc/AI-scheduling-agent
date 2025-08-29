# Scheduling Assistant

This Python script (`schedule.py`) is a scheduling assistant that integrates with Google Calendar to create events based on user input. It uses the Together AI API to parse natural language input and extract event details such as title, date, time, and location, then schedules the event on the user's Google Calendar.

## Features
- **Natural Language Parsing**: Uses Together AI's language model to interpret user input and extract event details (summary, date, time, location).
- **Google Calendar Integration**: Authenticates with Google Calendar API to create events in the user's primary calendar.
- **User Confirmation**: Displays extracted event details and allows the user to confirm or edit them before scheduling.
- **Fallback Parsing**: If the language model fails to parse input, a basic parsing method attempts to extract details.
- **Timezone Support**: Events are scheduled in the 'Asia/Kolkata' timezone (IST, UTC+5:30).

## Prerequisites
1. **Python Libraries**:
   - Install required packages using:
     ```bash
     pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dateutil together
     ```
2. **Google Calendar API Setup**:
   - Enable the Google Calendar API in the Google Cloud Console.
   - Download the OAuth 2.0 credentials file (`credentials.json`) and place it in the project directory.
   - Update the `CREDENTIALS_FILE` variable in `schedule.py` with the path to `credentials.json`.
3. **Together AI API Key**:
   - Obtain an API key from Together AI.
   - Set the `TOGETHER_API_KEY` environment variable:
     ```bash
     export TOGETHER_API_KEY="your_togetherai_api_key"
     ```
   - Alternatively, update the `TOGETHER_API_KEY` variable in `schedule.py` with your API key.

## Setup
1. Clone or download the script (`schedule.py`).
2. Ensure the credentials file (`credentials.json`) is in the correct path specified in `CREDENTIALS_FILE`.
3. Set the `TOKEN_FILE` path in `schedule.py` for storing OAuth tokens (e.g., `token.pickle`).
4. Install dependencies (see Prerequisites).
5. Set the Together AI API key as an environment variable or in the script.

## Usage
1. Run the script:
   ```bash
   python schedule.py
   ```
2. Follow the prompts:
   - Enter event details in natural language (e.g., "Team meeting tomorrow at 10 AM on Zoom").
   - Review the extracted details (title, date, time, location).
   - Confirm or edit the details.
   - The script will create the event in your Google Calendar and provide a link to the event.
3. To exit, type `exit` when prompted for event details.

## Example Input
```
Enter event details: Team meeting next Monday at 10 AM in Conference Room A
```
**Output**:
```
Extracted Event Details:
Title: Team meeting
Date: 2025-09-01
Time: 10:00
Location: Conference Room A

Are these details correct? (yes/no): yes
Event created: [Google Calendar event link]
```

## Notes
- The script assumes events are one hour long by default if no duration is specified.
- If the Together AI API fails to parse input, the script falls back to a basic parsing method that may not be as accurate.
- Ensure your system clock is accurate, as date parsing relies on it.
- The script uses the 'Asia/Kolkata' timezone. Modify the `timeZone` field in `create_google_calendar_event` if you need a different timezone.

## Limitations
- Requires a stable internet connection for API calls.
- The basic fallback parsing may not handle complex inputs well.
- The Together AI API key must be valid and have sufficient quota.
- Google Calendar API credentials must be properly configured.

## Troubleshooting
- **Credentials File Not Found**: Ensure `credentials.json` is in the specified path and the `CREDENTIALS_FILE` variable is correct.
- **Authentication Issues**: Delete `token.pickle` and rerun the script to re-authenticate.
- **API Key Error**: Verify the `TOGETHER_API_KEY` environment variable or the key in the script.
- **Parsing Errors**: If the LLM fails to parse input, provide clearer input or manually edit the details when prompted.

## License
This project is licensed under the MIT License.