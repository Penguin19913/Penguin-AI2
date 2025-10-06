from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

env_vars = dotenv_values(".env")

InputLanguage  = env_vars.get("InputLanguage")

# Define the HTML code for the speech recognition interface
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the html code with the input language
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';" )

# Write the modified HTML code to a file
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

# Get the current working directory
current_dir = os.getcwd()
# Generate the file path for the HTML file
Link = f"{current_dir}/Data/Voice.html"

# Set Chrome options for the WebDriver

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"

chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# initialize the chrome webdriver using the chromedrivermanager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# driver.get("https://httpbin.org/get")

# define path for temporary files
TempDirPath = rf"{current_dir}/Frontend/Files"

# function to set the assistant's status by writing it to a file
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# function to modify a query to ensure proper punctuation and formatting
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    # check if query is a question and add a question mark if necessary
    if any(word + ' ' in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # add a period if it is not a question
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

# function to translate text into english using the translate library
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# function to perform speech recognition using the webdriver
def SpeechRecognition():
    # open the html file in the browser
    driver.get("file:///"+ Link)
    # start speech recognition by clicking the start button 
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            # get the recognized text from the html output element
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                # stop recognition by clicking the stop button
                driver.find_element(by=By.ID, value="end").click()
                # if the input language is english, return the modified query
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    # if the input language is not english translate the text and return it
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            pass

if __name__=="__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
