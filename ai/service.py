import os

from dotenv import load_dotenv
from openai import OpenAI

from .config import AIConfig


class AI:

    def __init__(self, config=None):

        load_dotenv()

        self.config = config or AIConfig()

        api_key = os.getenv("API_KEY")

        if not api_key:
            raise ValueError(
                "API_KEY is not set"
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def chat(self, text):

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": self.config.system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        return response.choices[0].message.content