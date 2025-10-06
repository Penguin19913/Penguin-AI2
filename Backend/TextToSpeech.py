import pygame # for handling audio playback
import random 
import asyncio # for asynchronous operations
import edge_tts # for text to speech 
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# async function to convert text to an audio file
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3" # path where speech file will be saved 
    
    if os.path.exists(file_path): # check if the file already exists
        os.remove(file_path)
    
    # create the communicate object to generate speech
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+11%')
    await communicate.save(r'Data\speech.mp3') # save the generated audio 

# Function to manage text-to-speech functionality
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to an audio file async
            asyncio.run(TextToAudioFile(Text))

            # Initialize pygame mixer for audio playback
            pygame.mixer.init()

            # load the generated speech file into pygame mixer
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            # loop unitil the audio is done playing or the function stops 
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10) # limit loop to 10 ticks per second

            return True # return true if audio play successfully
        except Exception as e:
            print(f"Error in TTS: {e}")

        finally:
            try:
                # call the provided function with false to signal the end of tts
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            
            except Exception as e:
                print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)

    # otherwise just play the whole text
    else:
        TTS(Text, func)

if __name__=="__main__":
    while True:
        TextToSpeech(input("Enter the Text: "))
