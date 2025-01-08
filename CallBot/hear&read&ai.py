from gtts import gTTS
import os
import pygame
import requests
import speech_recognition as sr

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


def generate_response(text):
           
    ai_response = ""  

    try:
        response = "https://a.picoapps.xyz/ask-ai?prompt=${encodeURIComponent(' Answer my question : "  + text + "')}"
        # Send a request to the AI model
        response = requests.get(response)
        response = response.json()
        ai_response = response["response"]

    except Exception as e:
        print("Error generating response:", e)

    return ai_response


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

if __name__ == "__main__":
    while True:
        text = transcribe_until_silence()
        ai_response = generate_response(text)
        text_to_speech(ai_response)
    



