import os
import telegram
import openai
import anthropic
from flask import Flask, request

# Bot & API Keys
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Initialize Flask app
app = Flask(__name__)
bot = telegram.Bot(token=BOT_TOKEN)

# Function to generate a tricky, witty Yes/No poll question
def generate_poll_question(tweet_text):
    prompt = f"""
    Create a witty, spicy, tricky Yes/No poll question inspired by this tweet:
    '{tweet_text}'
    It should sound like a human asking and spark engagement.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert at crafting engaging, tricky Yes/No poll questions."},
                  {"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY
    )

    return response["choices"][0]["message"]["content"].strip()

# Root route
@app.route("/")
def root():
    return {"status": "Bot is running"}

# Webhook endpoint for IFTTT
@app.route("/new_tweet", methods=["POST"])
def new_tweet():
    data = request.json
    tweet_text = data.get("tweet", "")

    if tweet_text:
        poll_question = generate_poll_question(tweet_text)
        bot.send_poll(chat_id=CHANNEL_ID, question=poll_question, options=["Yes", "No"])

    return {"status": "success"}

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
