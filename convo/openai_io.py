from typing import List
import os
import openai


class OpenAIChatCompletion:
    def __init__(self):
        openai.api_key = os.environ["OPENAI_KEY"]

    def get_response(self, transcript: List[str]) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        for i, text in enumerate(reversed(transcript)):
            messages.insert(1, {"role": "user" if i % 2 == 0 else "assistant", "content": text})
        output = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        return output["choices"][0]["message"]["content"]
