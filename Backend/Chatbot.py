from groq import Groq # groq to use its api
from json import load, dump # to read and write JSON file
import datetime # for realtime date and time information
from dotenv import dotenv_values # to read environment variables from .env files

# load environment variables from the .env files
env_vars = dotenv_values(".env")

# retrieve specific environment variables
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

#Initialize the groq client 
client = Groq(api_key=GroqAPIKey)

#Initialize empty list to store chat messages
messages = []

# Define a system message that provides context to the AI chatbot about its role and behaviour
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only Hindi, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instructions for the chatbot
SystemChatBot = [
    {"role": "system", "content": System}
]

# attempt to load the chat log from a JSON file
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f) # Load existing messages from the chat log.
except FileNotFoundError: 
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# function to get real-time date and time information
def RealtimeInformation():
    current_dat_time = datetime.datetime.now()
    day = current_dat_time.strftime("%A")
    date = current_dat_time.strftime("%d")
    month = current_dat_time.strftime("%B")
    year = current_dat_time.strftime("%Y")
    hour = current_dat_time.strftime("%H")
    minute = current_dat_time.strftime("%M")
    second = current_dat_time.strftime("%S")

    # Format the information into a string
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n') # Split the responses into lines
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Main Chatbot function to handle user queries
def ChatBot(Query):
    """ This function send the user's query to the chatbot and returns the AI's response. """

    try:
        # Load the existing chat log from the JSON file.
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # append the user queries
        messages.append({"role": "user", "content": f"{Query}"})

        # make a request to the Groq API for a response
        completion = client.chat.completions.create(
            model="llama3-70b-8192", #   Specify the AI model to use
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages, # icludes system instruction, real-time info, and query
            max_tokens=1024, # Limit the maximum tokens in the response.
            temperature=0.7,
            top_p=1, # use nucleus sampling to control diversity
            stream=True, # Enable streaming response
            stop=None # allow the model to determine when to stop
        )

        Answer = "" # initialize empty string to store the AI's response

        # process the streamed response chunks.
        for chunk in completion: 
            if chunk.choices[0].delta.content: # check if there's content in the current chunk
                Answer += chunk.choices[0].delta.content # append the content to the answer
        
        Answer = Answer.replace("</s>", "") # Clean unwanted tokens from the response

        # Append the chatbot's response to the messages list 
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chatlog to the json file
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        # return the formatted response
        return AnswerModifier(Answer=Answer)
    except Exception as e:
        # handle errors by printing it and resetting the chat log
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query) # retry the query after resetting the log
    
if __name__ == "__main__":
    while True:
        user_input = input("User: ") # prompt the user for question
        print(ChatBot(user_input))