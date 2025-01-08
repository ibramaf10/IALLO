import json
import asyncio
import uuid
import aiohttp
from typing import List

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

 
    async def process_message(self, message: str):
        """Process user message and generate appropriate response"""
        try:
            message_type = await self.classify_message(message)
            self.user_messages.append(message)
            response = None

            if message_type == "R":  # RDV/Appointment
                system_prompt = f"""You are an AI callbot for {self.company} That handle RDVs and appointements section by asking 
                questions about details of the appointement in a short simple text paragraphe where you ask about the fullname of 
                the user, the email, the phone number, the subject of rdv, the timing and date of the meet, and if it is online 
                or inplace. and dont use numbers for questions, just ask diectly the question in a simple text form."""
                
                response = await self.connect_websocket(system_prompt, message, "R")
                self.websocket_response = response
                self.bot_messages.append(response)
                
            elif message_type == "C":  # Contact
                system_prompt = f"""You are an AI callbot for {self.company} That handle company communication and contact section 
                by asking questions about details of the message you need to deliver in form of short simple text paragraphe : 
                like the name of the user, the email, the phone number, the subject and the message"""
                
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
                    "email": "xxxx",
                    "phone": "xxxx",
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

                            email_body = f"""<br/> >> E-mail: {parsed_data['email']}
                                        <br/> >> Name: {parsed_data['name']}
                                        <br/> >> Phone: {parsed_data['phone']}
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

async def main():
    try:
        # Initialize callbot
        callbot = CompanyCallbot()
        
        # Load configuration
        await callbot.load_config('data.json')
        
        # Send welcome message
        print(f"\nBot: {callbot.welcome}\n")
        
        # Main chat loop
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() == 'quit':
                print("\nGoodbye!")
                break
                
            response = await callbot.process_message(user_input)

            if response:
                if isinstance(response, tuple) and response[1]:
                    print(f"\nBot: {response[0]}\n")
                    break


            print(f"\nBot: {response}\n")
            
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())