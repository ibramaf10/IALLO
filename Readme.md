# Speech Assistant with Twilio Voice and OpenAI Realtime API

This app uses Python, [Twilio Voice](https://www.twilio.com/docs/voice), [Media Streams](https://www.twilio.com/docs/voice/media-streams), and [OpenAI's Realtime API](https://platform.openai.com/docs/) to enable phone conversations with an AI Assistant. It sets up websockets to transfer voice audio between OpenAI and Twilio, handling inbound calls via a webhook in `index.py` that generates a TwiML response to connect the call to a media stream.

For a tutorial, visit [here](https://www.twilio.com/en-us/voice-ai-assistant-openai-realtime-api-python).

This app uses:
- Twilio Voice (TwiML, Media Streams)
- Twilio Phone Numbers
- OpenAI Realtime API

## Prerequisites

- **Python 3.9+** (We used `3.9.13`): [Download](https://www.python.org/downloads/).
- **Twilio account**: [Sign up](https://www.twilio.com/try-twilio).
- **Twilio number with Voice capabilities**: [Purchase](https://help.twilio.com/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console).
- **OpenAI account and API Key**: [Sign up](https://platform.openai.com/).

## Local Setup

Follow these steps to set up the app locally:

1. Run ngrok to expose your local server: [Download ngrok](https://ngrok.com/).
2. (Optional) Create a virtual environment.
3. Configure Twilio.
4. Configure OpenAI.
5. Update the .env file.
6. Install required packages.

### Open an ngrok tunnel

Run in Terminal:
python main.py index.py
