# I-AllO: Your Affordable CallBot Solution

With I-AllO, you can set up a cost-effective CallBot agent in minutes using Python, [Twilio Voice](https://www.twilio.com/docs/voice), [Media Streams](https://www.twilio.com/docs/voice/media-streams), and [OpenAI's Realtime API](https://platform.openai.com/docs/). 

This app facilitates phone conversations with an AI Assistant by establishing websockets to transfer voice audio between OpenAI and Twilio. 
It manages inbound and outbound calls through a webhook which generates a TwiML response to connect the call to a media stream.

I-AllO offers a range of solutions for various industries, including:

- **Customer Support**: Automate customer interactions and streamline support processes.
- **Sales Automation**: Enhance sales efficiency with AI-driven call handling.
- **Lead Generation**: Capture and qualify leads effectively.
- **Appointment Scheduling**: Simplify scheduling with automated call handling.
- **Voice Products**: Develop custom voice solutions tailored to your business needs.

I-AllO leverages:
- Twilio Voice (TwiML, Media Streams)
- Twilio Phone Numbers
- OpenAI Realtime API

## Prerequisites

- **Python 3.9+** (We used `3.9.13`): [Download](https://www.python.org/downloads/).
- **Twilio account**: [Sign up](https://www.twilio.com/try-twilio).
- **Twilio number with Voice capabilities**: [Purchase](https://help.twilio.com/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console).
- **OpenAI account and API Key**: [Sign up](https://platform.openai.com/).

## Local Setup

To set up I-AllO locally, follow these steps:

1. Run ngrok to expose your local server: [Download ngrok](https://ngrok.com/).
2. (Optional) Create a virtual environment.
3. Configure Twilio.
4. Configure OpenAI.
5. Update the .env file.
6. Install required packages.

### Open an ngrok tunnel

Execute in Terminal:
python main.py index.py


Additionally, I-AllO provides a variety of pricing plans to suit different business requirements, from the Starter plan with basic features to the Enterprise plan offering custom solutions and dedicated support. For more details, visit our website: [https://iallo.surge.sh](iallo.surge.sh).

For any inquiries or support, feel free to reach out through our contact [iallo@gmail.com](iallo@gmail.com). We are here to assist you in transforming your business with AI-powered call solutions.
