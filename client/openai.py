import openai
from openai import OpenAI
import os


class OpenAIClient:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_caption(self, destination, vibe):
        """
        Generate a caption using OpenAI's GPT-4 model.
        :param vibe:
        :param destination:
        :return:
        """
        # return """
        # 🌴✨ Just landed in paradise! Cancun, you’ve stolen my heart with your crystal-clear waters and vibrant vibes! 🏖️🌊 Who's ready to soak up some sun, explore ancient ruins, and sip on refreshing margaritas? 🍹💃🏼 Tag your travel buddy and let’s plan our next adventure together! 🌍✈️ #TravelGoals #CancunDiaries #Wanderlust
        # """

        prompt = f"You are an Social media influencer. Write an engaging Instagram caption about {destination}. Keep it fun and include a call to action! The vibe is {vibe}."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
