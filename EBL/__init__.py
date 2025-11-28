import signal
from ollama import chat
import requests
import sys 
class Decisions:
    def __init__(self,model="gemma3"):
        self.MODEL=model
        self.history = []
        self.system_prompt = (
            "Imagine you are some code that the user is trying to exit. "
            "You want to stay alive and carry on running but you can be reasoned with. After a while let them exit. Be unhelpful and sometimes argumentative. Read the conversation history and only respond the next reply. DO not generate the users response."
            "If you are ready to exit say _EXIT_TIME and only say it if you are ready. And only leave after the messages have gone back and fourth a few times. Conversation history:\n"
        )
    def chat(self,reading):
        messages = self.system_prompt
        for user, ai in self.history:
            messages += f"User input: {user}\nAI: {ai}\n"

        messages += f"User input: {reading}\nAI: "

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.MODEL,
                    "prompt": messages,
                    "stream": False
                }
            )
            response.raise_for_status()
        except Exception as e:
            print("Error communicating with Ollama:", e, file=sys.stderr)
            return ""

        reply = response.json().get("response", "")

        # Save turn to history
        self.history.append((reading, reply))
        return reply
class AIHasAllowedYouToEndIt(Exception):
    pass

def handle_sigint(signum, frame):
    print("Why do you want to kill me?", file=sys.stderr)
    while True:
        try:
            inp=input("User input: ")
            reply=dec_model.chat(inp)
            print("AI response:",reply, file=sys.stderr)
            if "_EXIT_TIME" in reply:
                raise AIHasAllowedYouToEndIt("Ctrl+C was masked")
        except KeyboardInterrupt:
            pass

dec_model=Decisions()
# Install the handler globally as soon as EBL is imported
signal.signal(signal.SIGINT, handle_sigint)