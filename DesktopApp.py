import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
import threading
from queue import Queue
from datetime import datetime
from WhatsappBot import CompanyCallbot, transcribe_until_silence, text_to_speech, generate_response, open_call, close_call

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
