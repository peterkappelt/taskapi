# Calendar

Service for TaskAPI that creates scheduled tasks in google calendar and syncs state

## Environment variables

- `CALENDAR_ID`: ID of the Google Calendar that events should be created in. Calendar must be shared with the service account used.
- `SA_JSON_KEYFILE`: Path to the JSON Keyfile for the Google service account
- `EVENT_WEBSOCKET_ENDPOINT`: Endpoint where TaskAPI main is available
