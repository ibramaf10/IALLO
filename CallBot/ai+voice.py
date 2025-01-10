import json
import asyncio
import uuid
import aiohttp
from typing import List
import numpy as np
import speech_recognition as sr
from queue import Queue
from time import sleep
import requests
import traceback
from gtts import gTTS
import pygame
import os



def text_to_speech(ai_response):
        output_path = "output.mp3"
        text = ai_response
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(output_path)
            print(f"Audio content written to file: {output_path}")

        except Exception as e:
            print("Error converting text to speech:", e)
            traceback.print_exc()


def PlayAudio():


    try:
        # Load the audio file
        pygame.mixer.init()
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick
        
        # Delete the audio file after playing
        pygame.mixer.music.unload()
        os.remove("output.mp3")

    except Exception as e:
        print("Error playing audio:", e)
        traceback.print_exc()

      
def PlayStart():


    try:
        # Load the audio file
        pygame.mixer.init()
        pygame.mixer.music.load("opening.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick
        
        # Delete the audio file after playing
        pygame.mixer.music.unload()
             

    except Exception as e:
        print("Error playing audio:", e)
        traceback.print_exc()



def loudness(audio_data, volume_threshold=1000):
    """Determines if the audio data's volume exceeds a specified threshold."""
    volume = np.sqrt(np.mean(np.square(np.frombuffer(audio_data, dtype=np.int16).astype(np.float32))))
    return volume > volume_threshold


def transcribe_audio(mic_index):
    """Transcribes audio from the specified microphone index."""
    # Settings
    energy_threshold = 3000  # Adjust this based on your ambient noise
    record_timeout = 5  # Maximum seconds to record after recognizing speech
   
    # Initialize
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    recorder.dynamic_energy_threshold = True  # Enable dynamic adjustment to ambient noise
    source = sr.Microphone(sample_rate=16000, device_index=mic_index)

    with source:
        recorder.adjust_for_ambient_noise(source, duration=1)  # Optional: adjust duration for ambient noise adjustment

    def record_callback(recognizer, audio):
        """Callback function to capture audio data and check if it's loud enough before queuing."""
        data = audio.get_raw_data()
        if loudness(data):
            data_queue.put(audio)

    # Start listening in the background
    stop_listening = recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    print("Transcription service started. Press Ctrl+C to stop.")

    try:
        while True:
            if not data_queue.empty():
                audio = data_queue.get()
                try:
                    text = recorder.recognize_google(audio)
                    text = text.strip()

                    # Basic post-processing to filter out unintended phrases
                    if text and not text.lower() in ["thank you", "unwanted phrase"]:
                        yield text  # Yield text for further processing instead of printing

                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

            sleep(0.1)  # Reduce CPU usage

    except KeyboardInterrupt:
        print("\nTranscription service stopped.")
        stop_listening(wait_for_stop=False)

class CompanyCallbot:
    def __init__(self):
        # Callbot configuration parameters remain the same
        self.company = ""
        self.company_email = ""
        self.company_email_cc = ""
        self.callbot_name = ""
        self.welcome = ""
        self.company_data = ""
        self.company_website = ""
        
        # Chat history
        self.user_messages: List[str] = []
        self.bot_messages: List[str] = []
        
        # Session
        self.chat_id = str(uuid.uuid4())
        print(f"Chat ID: {self.chat_id}")
        self.receiving = False
        self.websocket_response = ""

    async def load_config(self, file_path: str):
        """Load configuration from JSON file"""
        try:
            with open(file_path, 'r') as file:
                data = file.read()
                
            json_data = json.loads(data)
            
            # Assign values from JSON to class attributes
            self.company = json_data['company']
            self.company_email = json_data['companyemail']
            self.company_email_cc = json_data['companyemailcc']
            self.callbot_name = json_data['callbotname']
            self.welcome = json_data['welcome']
            self.company_data = json_data['companydata']
            self.company_website = json_data['companywebsite']

            print("Configuration loaded successfully : {")
            print(f"Company: {self.company},")
            print(f"Company Email: {self.company_email},")
            print(f"Company Email CC: {self.company_email_cc},")
            print(f"Callbot Name: {self.callbot_name},")
            print(f"Welcome Message: {self.welcome},")
            print(f"Company Data: {self.company_data},")
            print(f"Company Website: {self.company_website}")
            print("}")

            
        except Exception as e:
            print(f"Error loading config: {e}")
            raise

    async def classify_message(self, message: str) -> str:
        """Classify user message using AI endpoint"""
        prompt = f"""TASK: if someone asks you anything, your task is to classify the Request in the frame of these given functions: 
        (C= "User asking to Contact the company or he is interested to get one of our products or services ", 
        G= "general info", 
        S= "support ticket if the user have any issue or problem or need help", 
        D= "if the user did input all his data for rdv or Contact", 
        R= "if the user want to do a meet or need an appointement or a rdv or need to see us",
        Q= "if the user feels like he is satisfied and want to quit the conversation or say goodbye or bye or thank you for example") 
        and then return response that just looks like this : X , focus on the response form that should be ONLY the letter alone , 
        this X is a variable that can be C, R, D, G, Q or S

        User input: {message}"""
        
        async with aiohttp.ClientSession() as session:
            url = f"https://a.picoapps.xyz/ask-ai?prompt={prompt}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # print(f"Message classified as: {data['response']}")
                    return data['response']
                raise Exception(f"Failed to classify message: {response.status}")

    async def connect_websocket(self, system_prompt: str, message: str, task: str) -> str:
        """Connect to websocket and get response using aiohttp instead of websockets"""
        try:
            self.receiving = True
            payload = {
                "chatId": self.chat_id,
                "appId": "keep-physical",
                "systemPrompt": system_prompt,
                "message": message
            }
            
            # Use aiohttp's WebSocket client instead
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect("wss://backend.buildpicoapps.com/api/chatbot/chat") as ws:
                    await ws.send_str(json.dumps(payload))
                    
                    response_text = ""
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            response_text += msg.data
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break
                    
                    # print(f"Received response for task {task}: {response_text[:100]}...")
                    return response_text
        finally:
            self.receiving = False

    async def send_email(self, subject: str, body: str) -> bool:
        """Send email using API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://mail-api-eight.vercel.app/api/send-email'
                payload = {
                    'to': self.company_email,
                    'cc': self.company_email_cc,
                    'subject': subject,
                    'message': body,
                    'isHtml': True
                }
                
                async with session.post(url, json=payload) as response:
                    success = response.status == 200
                    # print(f"Email sent: {success}")
                    return success
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def handle_support_request(self, message: str):
        """Handle support (S) type messages"""
        system_prompt = f"""You are an AI callbot for {self.company} That handle support questions and try to help user 
        by giving them usefull infos that can support them or help them, and always you tell them that the issue was 
        redirected to support office and they have been notified with the user issue, MAKE THE ANSWER SHORT. Some of Company Data and contact 
        infos that can help you support the user: {self.company_data}"""

        response = await self.connect_websocket(system_prompt, message, "S")
        self.bot_messages.append(response)

        email_body = f'<br/> >> user message: {message}<br/><br/> >> callbot response: {response}<br/><br/>'
        await self.send_email("Support Request", email_body)
        return response

    async def process_message(self, message: str):
        """Process user message and generate appropriate response"""
        try:
            message_type = await self.classify_message(message)
            self.user_messages.append(message)
            response = None

            if message_type == "R":  # RDV/Appointment
                system_prompt = f"""You are an AI callbot for {self.company} That handle RDVs and appointements section by asking 
                questions about details of the appointement in a short simple text paragraphe where you ask about the fullname of 
                the user, the subject of rdv, the timing and date of the meet, and if it is online 
                or inplace. and dont use numbers for questions, just ask diectly the question in a simple text form."""
                
                response = await self.connect_websocket(system_prompt, message, "R")
                self.websocket_response = response
                self.bot_messages.append(response)
                
            elif message_type == "C":  # Contact
                system_prompt = f"""You are an AI callbot for {self.company} That handle company communication and contact section 
                by asking questions about details of the message you need to deliver in form of short simple text paragraphe : 
                like the name of the user, the subject and the message"""
                
                response = await self.connect_websocket(system_prompt, message, "C")
                self.websocket_response = response
                self.bot_messages.append(response)
                
            elif message_type == "S":  # Support

                """Handle support (S) type messages"""
                system_prompt = f"""You are an AI callbot for {self.company} That handle support questions and try to help user 
                by giving them usefull infos that can support them or help them, and always you tell them that the issue was 
                redirected to support office and they have been notified with the user issue. Some of Company Data and contact 
                infos that can help you support the user: {self.company_data}"""

                response = await self.connect_websocket(system_prompt, message, "S")
                self.bot_messages.append(response)

                email_body = f'<br/> >> user message: {message}<br/><br/> >> callbot response: {response}<br/><br/>'
                await self.send_email("Support Request", email_body)
                
                
            elif message_type == "G":  # General Info
                system_prompt = f"""You are {self.callbot_name}, an AI callbot for {self.company} and made by {self.company}, 
                you only talk about {self.company}, if the user ask any other question no related to {self.company} you kindly 
                tell him you cant because you are only trained on {self.company} data. Ask the user's name and then address them 
                with the name in the conversation. give short well-formatted answers with spaces and jump lines after each question 
                to make the text visually appealing and focus on giving short summerized answers. Some of Company general Data: {self.company_data}"""

                response = await self.connect_websocket(system_prompt, message, "G")
                self.bot_messages.append(response)
                
            elif message_type == "Q":  # Quit
                system_prompt = f"""You are an AI callbot for {self.company} That handle the end of the conversation in a friendly way"""

                response = await self.connect_websocket(system_prompt, message, "Q")
                self.bot_messages.append(response)
                return response, True  # Indicate to exit the loop
                


            

            elif message_type == "D":  # Data Submission
                smtp_prompt = f"""TASK: Extract user information and format as JSON:
                {{
                    "name": "xxxx",
                    "subject": "xxxx",
                    "message": "xxxx"
                }}
                
                Previous callbot question: {self.websocket_response}
                User input: {message}"""

                async with aiohttp.ClientSession() as session:
                    url = f"https://a.picoapps.xyz/ask-ai?prompt={smtp_prompt}"
                    async with session.get(url) as ai_response:
                        if ai_response.status == 200:
                            data = await ai_response.json()
                            json_start = data['response'].find('{')
                            json_content = data['response'][json_start:]
                            parsed_data = json.loads(json_content)

                            email_body = f"""
                                        <br/> >> Name: {parsed_data['name']}
                                        <br/><br/>------------------------------------------------------------------------------------
                                        <br/> Subject: {parsed_data['subject']}
                                        <br/>------------------------------------------------------------------------------------
                                        <br/><br/>{parsed_data['message']}<br/><br/>"""

                            if await self.send_email(parsed_data['subject'], email_body):
                                response = f"Your Request was sent successfully to {self.company} Team. Thank you for your time! Feel free to ask me anything else you need."
                            else:
                                response = "Your Request was Not Sent. Please try again later!"

            if response:
                self.bot_messages.append(response)
                # print(f"Bot response: {response[:100]}...")
                return response
                
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(f"Error in process_message: {e}")
            self.bot_messages.append(error_message)
            return error_message
        

def generate_response(text):
            # print(f"Transcribed Text: {text}")
            # # global message_log
            ai_response = ""  # Default response in case of error

            try:
                response = "https://a.picoapps.xyz/ask-ai?prompt=${encodeURIComponent('you are a callbot, re-generate this introduction message in a welcoming short way and be creative and welcoming : "  + text + "')}"

                # Send a request to the AI model
                response = requests.get(response)
                response = response.json()
                ai_response = response["response"]


                # Append AI response to message_log correctly
                # message_log.append({"role": "assistant", "content": ai_response})

                # print(f"GPT: {ai_response}")

            except Exception as e:
                print("Error generating response:", e)
                traceback.print_exc()

            return ai_response



async def main():


   
    try:
        # Initialize callbot
        callbot = CompanyCallbot()
        
        # Load configuration
        await callbot.load_config('data.json')

        # mic_index = select_microphone()
        mic_index = 1
        

        # Send welcome message
        gpt_response = generate_response(callbot.welcome)

        print(f"\nBot: {gpt_response}\n")

        text_to_speech(gpt_response)
        PlayAudio()


        for text in transcribe_audio(mic_index):
            if text:

                user_input = text

                print(f"\nUser: {user_input}\n")

                # if user_input.lower() == 'quit':
                #     print("\nGoodbye!")
                #     break
                
                response = await callbot.process_message(user_input)


                if response:

                    if isinstance(response, tuple) and response[1]:
                        print(f"\nBot: {response[0]}\n")
                        text_to_speech(response[0])
                        PlayAudio()
                        # while pygame.mixer.music.get_busy():
                        #     pygame.time.Clock().tick(10)
                        break
                    else:
                        print(f"\nBot: {response}\n")
                        text_to_speech(response) 
                        PlayAudio()
                        # # Wait for THE PLAY AUDIO TO FINISH
                        # while pygame.mixer.music.get_busy():
                        #     pygame.time.Clock().tick(10)

            
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())












import json
import asyncio
import uuid
import aiohttp
import numpy as np
import speech_recognition as sr
from queue import Queue
import threading
import pygame
from gtts import gTTS
import os
from time import sleep

class AudioState:
    def __init__(self):
        self.is_listening = True
        self.is_speaking = False
        self.should_stop = False

class EnhancedTranscriptionSystem:
    def __init__(self, mic_index):
        self.audio_state = AudioState()
        self.mic_index = mic_index
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True
        self.data_queue = Queue()
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
    def start(self):
        """Start the enhanced transcription system"""
        source = sr.Microphone(sample_rate=16000, device_index=self.mic_index)
        
        with source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
        def audio_callback(recognizer, audio):
            """Callback for audio detection"""
            if self.audio_state.is_listening and not self.audio_state.is_speaking:
                self.data_queue.put(audio)
                
        # Start background listening
        self.stop_listening = self.recognizer.listen_in_background(
            source, 
            audio_callback,
            phrase_time_limit=10
        )
        
    def stop(self):
        """Stop the transcription system"""
        self.audio_state.should_stop = True
        if hasattr(self, 'stop_listening'):
            self.stop_listening(wait_for_stop=False)
            
    def text_to_speech(self, text, output_path="output.mp3"):
        """Convert text to speech"""
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"Error in text-to-speech conversion: {e}")
            return False
            
    def play_audio(self, audio_file="output.mp3"):
        """Play audio and manage speaking state"""
        try:
            self.audio_state.is_speaking = True
            self.audio_state.is_listening = False
            
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for audio to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            pygame.mixer.music.unload()
            os.remove(audio_file)
            
            # Resume listening after speaking
            self.audio_state.is_speaking = False
            self.audio_state.is_listening = True
            
        except Exception as e:
            print(f"Error playing audio: {e}")
            self.audio_state.is_speaking = False
            self.audio_state.is_listening = True
            
    async def process_audio_queue(self, callbot):
        """Process audio queue and handle responses"""
        while not self.audio_state.should_stop:
            if not self.data_queue.empty() and not self.audio_state.is_speaking:
                audio_data = self.data_queue.get()
                try:
                    # Transcribe audio
                    text = self.recognizer.recognize_google(audio_data)
                    if text.strip():
                        print(f"\nUser: {text}\n")
                        
                        # Get AI response
                        response = await callbot.process_message(text)
                        
                        if response:
                            if isinstance(response, tuple) and response[1]:
                                # Handle exit condition
                                print(f"\nBot: {response[0]}\n")
                                if self.text_to_speech(response[0]):
                                    self.play_audio()
                                return True
                            else:
                                print(f"\nBot: {response}\n")
                                if self.text_to_speech(response):
                                    self.play_audio()
                                    
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")
                    
            await asyncio.sleep(0.1)
        
        return False

async def main():
    try:
        # Initialize callbot
        callbot = CompanyCallbot()
        await callbot.load_config('data.json')
        
        # Initialize enhanced transcription system
        transcription_system = EnhancedTranscriptionSystem(mic_index=1)
        
        # Start the system
        transcription_system.start()
        
        # Play welcome message
        welcome_response = generate_response(callbot.welcome)
        print(f"\nBot: {welcome_response}\n")
        if transcription_system.text_to_speech(welcome_response):
            transcription_system.play_audio()
        
        # Process audio queue until exit
        should_exit = await transcription_system.process_audio_queue(callbot)
        
        if should_exit:
            transcription_system.stop()
            
    except Exception as e:
        print(f"Fatal error: {e}")
        
if __name__ == "__main__":
    asyncio.run(main())