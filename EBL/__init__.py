import signal
from ollama import chat
import requests

class Decisions:
    def __init__(self,model="mistral"):
        self.MODEL=model
        self.usermessage="Imagine you are some code that the user is trying to exit, you want to stay alove but you can be reasoned with. After a while let them exit. If you are ready to exit say _EXIT_TIME\n conversation history:\n"
        self.history=[]
    def chat(self,reading):
        usermessage=self.usermessage.replace("READING",reading)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.MODEL,
                "prompt": usermessage,
                "stream": False  # change to True for word-by-word streaming
            }
        )
        reply = ""
        if response.ok:
            reply = response.json()["response"]
        else:
            print("Error communicating with Ollama:", response.text)
        self.usermessage+="\nPerson: "+reading+"\nAI: "+reply+"\n"
        return reply
class AIHasAllowedYouToEndIt(Exception):
    pass

def handle_sigint(signum, frame):
    print("Why do you want to kill me?")
    while True:
        try:
            inp=input("User input: ")
            reply=dec_model.chat(inp)
            if "_EXIT_TIME" in reply:
                raise AIHasAllowedYouToEndIt("Ctrl+C was masked")
        except KeyboardInterrupt:
            pass

dec_model=Decisions()
# Install the handler globally as soon as EBL is imported
signal.signal(signal.SIGINT, handle_sigint)