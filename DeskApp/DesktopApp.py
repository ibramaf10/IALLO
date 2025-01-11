import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
import threading
from queue import Queue
from datetime import datetime
import json
import asyncio
import uuid
import aiohttp
from typing import List
import speech_recognition as sr
from time import sleep
import requests
import traceback
from gtts import gTTS
import pygame
import os
import subprocess
import pyautogui


def open_call(phone):

    phone_number = phone  # Replace with the actual phone number

    try:
        subprocess.run(["cmd", "/c", f"start whatsapp://send?phone={phone_number}"], check=True)
        subprocess.run(["cmd", "/c", f"start whatsapp://send?phone={phone_number}"], check=True)
        print(f"Calling {phone_number} on WhatsApp...")
        sleep(3) 
        pyautogui.click(x=1280, y=70) 
        pyautogui.click(x=1280, y=70) 
    except Exception as e:
        print(f"Failed to open WhatsApp and call the number: {e}")


def transcribe_until_silence():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        # recognizer.adjust_for_ambient_noise(source, duration=2)

        try:
            print("Listening...")
            
            audio = recognizer.listen(source)

            # Transcribe the speech
            transcript = recognizer.recognize_google(audio)
            # print(f"Transcribed text: {transcript}")
            return transcript


        except sr.RequestError as e:
            print(f"API error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")
    
    # Initialize pygame mixer
    pygame.mixer.init()
    
    # Load and play the mp3 file
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    
    # Wait for the music to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Stop the mixer and delete the mp3 file

    pygame.mixer.music.stop()
    pygame.mixer.quit()
    os.remove("output.mp3")


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

            # print("Configuration loaded successfully : {")
            # print(f"Company: {self.company},")
            # print(f"Company Email: {self.company_email},")
            # print(f"Company Email CC: {self.company_email_cc},")
            # print(f"Callbot Name: {self.callbot_name},")
            # print(f"Welcome Message: {self.welcome},")
            # print(f"Company Data: {self.company_data},")
            # print(f"Company Website: {self.company_website}")
            # print("}")

            
        except Exception as e:
            print(f"Error loading config: {e}")
            raise

    async def classify_message(self, message: str) -> str:
        """Classify user message using AI endpoint"""
        prompt = f"""TASK: if someone asks you anything, your task is to classify the Request in the frame of these given functions: 
        (C= "User asking to Contact the company or he is interested to get one of our products or services ", 
        G= "general info", 
        S= "support ticket if the user have any issue or problem or need help", 
        D= "if the user did input all his data (mail or phone) for rdv or Contact", 
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
                    print(f"Message classified as: {data['response']}")
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

   
    async def process_message(self, message: str):
        """Process user message and generate appropriate response"""
        try:
            message_type = await self.classify_message(message)
            self.user_messages.append(message)
            response = None

            if message_type == "R":  # RDV/Appointment
                system_prompt = f"""You are an AI callbot for {self.company} That handle RDVs and appointements section by asking 
                questions about details of the appointement in a short simple text paragraphe where you ask about the fullname of 
                the user, the subject of rdv, email, the timing and date of the meet, and if it is online 
                or inplace. and dont use numbers for questions, MAKE THE ANSWER VERY SHORT, just ask diectly the question in a simple text form."""
                
                response = await self.connect_websocket(system_prompt, message, "R")
                self.websocket_response = response
                self.bot_messages.append(response)
                
            elif message_type == "C":  # Contact
                system_prompt = f"""You are an AI callbot for {self.company} That handle company communication and contact section 
                by asking questions about details of the message you need to deliver in form of short simple text paragraphe MAKE IT VERY SHORT : 
                like the name of the user, the email and the subject and the message"""
                
                response = await self.connect_websocket(system_prompt, message, "C")
                self.websocket_response = response
                self.bot_messages.append(response)
                
            elif message_type == "S":  # Support

                """Handle support (S) type messages"""
                system_prompt = f"""You are an AI callbot for {self.company} That handle support questions and try to help user 
                by giving them usefull infos that can support them or help them, and always you tell them that the issue was 
                redirected to support office and they have been notified with the user issue MAKE THE ANSWER VERY SHORT, . Some of Company Data and contact 
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
                to make the text visually appealing and focus on giving short summerized answers MAKE THE ANSWER VERY SHORT,. Some of Company general Data: {self.company_data}"""

                response = await self.connect_websocket(system_prompt, message, "G")
                self.bot_messages.append(response)
                
            elif message_type == "Q":  # Quit
                system_prompt = f"""You are an AI callbot for {self.company} That handle the end of the conversation in a friendly way MAKE IT VERY SHORT """

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
                response = "https://a.picoapps.xyz/ask-ai?prompt=${encodeURIComponent('You are a Callbot, re-generate this introduction message in a welcoming way: "  + text + "')}"

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


def close_call():
    try:
        # screen_width, screen_height = pyautogui.size()
        # pyautogui.click(x=screen_width - 10, y=10)
        # print("Call ended.")
        # subprocess.run(["taskkill", "/F", "/IM", "WhatsApp.exe"], check=True)
        print("Call ended.")

    except Exception as e:
        print(f"Failed to close the call: {e}")



class CallbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("I-AllO WhatsApp Callbot")
        self.root.geometry("400x400")
        
        # Create message queue for communication between async and GUI
        self.message_queue = Queue()
        
        # Initialize callbot
        self.callbot = CompanyCallbot()
        
        self.setup_gui()
        self.setup_async_loop()
        
        # Start queue checker
        self.check_queue()

    def setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Phone number input
        phone_frame = ttk.Frame(main_frame)
        phone_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        ttk.Label(phone_frame, text="Phone Number:").grid(row=0, column=0, padx=5)
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(phone_frame, textvariable=self.phone_var, width=30)
        self.phone_entry.grid(row=0, column=1, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Call", command=self.start_call)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="End Call", command=self.end_call, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Chat log
        log_frame = ttk.LabelFrame(main_frame, text="Chat Log", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.chat_log = scrolledtext.ScrolledText(log_frame, width=70, height=20)
        self.chat_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

    def setup_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def log_message(self, message, sender="System"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_log.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        self.chat_log.see(tk.END)

    async def run_callbot(self, phone_number):
        try:
            # Load configuration
            await self.callbot.load_config('data.json')
            
            # Open WhatsApp call
            open_call(phone_number)
            self.message_queue.put(("status", "Call initiated..."))
            
            # Send welcome message
            welcome_response = generate_response(self.callbot.welcome)
            self.message_queue.put(("bot", welcome_response))
            text_to_speech(welcome_response)
            
            while True:
                text = transcribe_until_silence()
                if text:
                    self.message_queue.put(("user", text))
                    
                    response = await self.callbot.process_message(text)
                    
                    if isinstance(response, tuple) and response[1]:
                        self.message_queue.put(("bot", response[0]))
                        text_to_speech(response[0])
                        close_call()
                        break
                    else:
                        self.message_queue.put(("bot", response))
                        text_to_speech(response)
                
        except Exception as e:
            self.message_queue.put(("error", f"Error: {str(e)}"))
        finally:
            self.message_queue.put(("complete", None))

    def start_call(self):
        phone = self.phone_var.get().strip()
        if not phone:
            self.log_message("Please enter a phone number", "Error")
            return
            
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Call in progress...")
        
        def run_async():
            self.loop.run_until_complete(self.run_callbot(phone))
            
        thread = threading.Thread(target=run_async)
        thread.start()

    def end_call(self):
        close_call()
        self.loop.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Call ended")
        self.log_message("Call ended")
        self.loop.call_soon_threadsafe(self.loop.stop)
        

    def check_queue(self):
        try:
            while not self.message_queue.empty():
                msg_type, msg = self.message_queue.get_nowait()
                
                if msg_type == "user":
                    self.log_message(msg, "User")
                elif msg_type == "bot":
                    self.log_message(msg, "Bot")
                elif msg_type == "status":
                    self.status_var.set(msg)
                elif msg_type == "error":
                    self.log_message(msg, "Error")
                elif msg_type == "complete":
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.status_var.set("Ready")
                    
        except Exception as e:
            print(f"Error in check_queue: {e}")
            
        finally:
            self.root.after(100, self.check_queue)

def main():
    root = tk.Tk()
    app = CallbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
