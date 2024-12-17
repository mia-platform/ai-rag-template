import tkinter as tk
from tkinter import scrolledtext
import os

import requests
from dotenv import load_dotenv

load_dotenv()

server_url = os.getenv("SERVER_URL", "http://localhost:3000")
MIA_ASSISTANT_COMPLETION_ENDPOINT = "/chat/completions"

class ChatbotClient:
    def __init__(self, url):
        self.url = url

    def send_message(self, message, chat_history):
        response = requests.post(
            f"{self.url}{MIA_ASSISTANT_COMPLETION_ENDPOINT}",
            json={
                "chat_query": message,
                "chat_history": chat_history
            },
            headers={"Accept": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return f"Error: {response.text}"

class ChatApp:
    def __init__(self, root, chatbot_client):
        self.root = root
        self.chatbot_client = chatbot_client
        self.chat_history = []
        self.create_widgets()

    def create_widgets(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.text_area = scrolledtext.ScrolledText(self.root, state='disabled')
        self.text_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        self.input_text = scrolledtext.ScrolledText(self.root)
        self.input_text.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.send_button = tk.Button(self.root, text="Send", command=self.send)
        self.send_button.grid(row=1, column=1, pady=10, sticky='s')
        self.send_button.config(width=20, height=2)
        
    def _append_references(self, references):
        if(len(references) > 0):
            self.update_chat_history("References:")
        for reference in references:
            self.update_chat_history(f"- {reference['url']}")

    def send(self):
        message = self.input_text.get('1.0', tk.END)
        if message:
            self.update_chat_history("You: " + message)
            response = self.chatbot_client.send_message(message, self.chat_history)
            response_message = response['message']
            references = response['references']

            self.chat_history.append("You: " + message + "\n")
            self.chat_history.append(response_message)
            self.update_chat_history("Bot: " + response_message + "\n")
            self._append_references(references)
            self.input_text.delete('1.0', tk.END)

    def update_chat_history(self, message):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.configure(state='disabled')
        self.text_area.see(tk.END)

def main():
    root = tk.Tk()
    root.title("Chat with Bot")

    client = ChatbotClient(server_url)

    ChatApp(root, client)
    root.mainloop()

if __name__ == "__main__":
    main()
