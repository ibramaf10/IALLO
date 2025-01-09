from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import websockets
import json
import os
import base64
from dotenv import load_dotenv
import aiohttp
from typing import Dict, Optional

# Load environment variables
load_dotenv()

# Get OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print('Missing OpenAI API key. Please set it in the .env file.')
    exit(1)

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
SYSTEM_MESSAGE = '''You are an AI receptionist for Barts Automotive. Your job is to politely engage with the client and obtain their name, availability, and service/work required. Ask one question at a time. Do not ask for other contact information, and do not check availability, assume we are free. Ensure the conversation remains friendly and professional, and guide the user to provide these details naturally. If necessary, ask follow-up questions to gather the required information.'''
VOICE = 'alloy'
PORT = int(os.getenv('PORT', '5050'))
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Session management
sessions: Dict[str, dict] = {}

# List of Event Types to log
LOG_EVENT_TYPES = [
    'response.content.done',
    'rate_limits.updated',
    'response.done',
    'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped',
    'input_audio_buffer.speech_started',
    'session.created',
    'response.text.done',
    'conversation.item.input_audio_transcription.completed'
]

# Root route
@app.get("/")
async def root():
    return {"message": "Twilio Media Stream Server is running!"}

# Twilio incoming call route
@app.route("/incoming-call", methods=["GET", "POST"])
async def incoming_call(request: Request):
    print('Incoming call')
    host = request.headers.get('host')
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
                        <Response>
                            <Say>Hi, you have called Bart's Automative Centre. How can we help?</Say>
                            <Connect>
                                <Stream url="wss://{host}/media-stream" />
                            </Connect>
                        </Response>"""
    return Response(content=twiml_response, media_type="text/xml")

# WebSocket endpoint for media streaming
@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    await websocket.accept()
    print('Client connected')

    session_id = websocket.headers.get('x-twilio-call-sid') or f"session_{int(time.time())}"
    session = sessions.get(session_id, {'transcript': '', 'stream_sid': None})
    sessions[session_id] = session

    # Connect to OpenAI WebSocket
    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
        extra_headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'OpenAI-Beta': 'realtime=v1'
        }
    ) as openai_ws:
        
        # Send session update
        session_update = {
            'type': 'session.update',
            'session': {
                'turn_detection': {'type': 'server_vad'},
                'input_audio_format': 'g711_ulaw',
                'output_audio_format': 'g711_ulaw',
                'voice': VOICE,
                'instructions': SYSTEM_MESSAGE,
                'modalities': ['text', 'audio'],
                'temperature': 0.8,
                'input_audio_transcription': {
                    'model': 'whisper-1'
                }
            }
        }
        await openai_ws.send(json.dumps(session_update))

        try:
            # Handle WebSocket messages
            while True:
                try:
                    # Receive message from either WebSocket
                    twilio_message = await websocket.receive_text()
                    data = json.loads(twilio_message)

                    if data['event'] == 'media':
                        audio_append = {
                            'type': 'input_audio_buffer.append',
                            'audio': data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        session['stream_sid'] = data['start']['streamSid']
                        print(f'Incoming stream has started: {session["stream_sid"]}')
                    
                    # Handle OpenAI messages
                    openai_message = await openai_ws.recv()
                    response = json.loads(openai_message)

                    if response['type'] in LOG_EVENT_TYPES:
                        print(f'Received event: {response["type"]}', response)

                    if response['type'] == 'conversation.item.input_audio_transcription.completed':
                        user_message = response['transcript'].strip()
                        session['transcript'] += f'User: {user_message}\n'
                        print(f'User ({session_id}): {user_message}')

                    if response['type'] == 'response.done':
                        agent_message = next(
                            (content['transcript'] for output in response['response']['output']
                             for content in output.get('content', [])
                             if 'transcript' in content),
                            'Agent message not found'
                        )
                        session['transcript'] += f'Agent: {agent_message}\n'
                        print(f'Agent ({session_id}): {agent_message}')

                    if response['type'] == 'response.audio.delta' and response['delta']:
                        audio_delta = {
                            'event': 'media',
                            'streamSid': session['stream_sid'],
                            'media': {'payload': base64.b64encode(base64.b64decode(response['delta'])).decode()}
                        }
                        await websocket.send_text(json.dumps(audio_delta))

                except websockets.exceptions.ConnectionClosed:
                    break
                except Exception as e:
                    print(f'Error processing message: {e}')

        finally:
            # Clean up on disconnect
            print(f'Client disconnected ({session_id})')
            print('Full Transcript:')
            print(session['transcript'])
            
            await process_transcript_and_send(session['transcript'], session_id)
            sessions.pop(session_id, None)

async def make_chat_gpt_completion(transcript: str):
    print('Starting ChatGPT API call...')
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-2024-08-06',
                'messages': [
                    {'role': 'system', 'content': 'Extract customer details: name, availability, and any special notes from the transcript.'},
                    {'role': 'user', 'content': transcript}
                ],
                'response_format': {
                    'type': 'json_schema',
                    'json_schema': {
                        'name': 'customer_details_extraction',
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'customerName': {'type': 'string'},
                                'customerAvailability': {'type': 'string'},
                                'specialNotes': {'type': 'string'}
                            },
                            'required': ['customerName', 'customerAvailability', 'specialNotes']
                        }
                    }
                }
            }
        ) as response:
            data = await response.json()
            print('ChatGPT API response:', json.dumps(data, indent=2))
            return data

async def send_to_webhook(payload: dict):
    print('Sending data to webhook:', json.dumps(payload, indent=2))
    async with aiohttp.ClientSession() as session:
        async with session.post(
            WEBHOOK_URL,
            headers={'Content-Type': 'application/json'},
            json=payload
        ) as response:
            if response.status == 200:
                print('Data successfully sent to webhook.')
            else:
                print(f'Failed to send data to webhook: {response.status}')

async def process_transcript_and_send(transcript: str, session_id: Optional[str] = None):
    print(f'Starting transcript processing for session {session_id}...')
    try:
        result = await make_chat_gpt_completion(transcript)
        
        if result.get('choices') and result['choices'][0].get('message', {}).get('content'):
            try:
                parsed_content = json.loads(result['choices'][0]['message']['content'])
                print('Parsed content:', json.dumps(parsed_content, indent=2))
                await send_to_webhook(parsed_content)
                print('Extracted and sent customer details:', parsed_content)
            except json.JSONDecodeError as e:
                print('Error parsing JSON from ChatGPT response:', e)
        else:
            print('Unexpected response structure from ChatGPT API')
    except Exception as e:
        print('Error in process_transcript_and_send:', e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
