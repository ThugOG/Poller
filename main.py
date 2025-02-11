import os
import openai
import requests
from flask import Flask, request, jsonify
from telegram import Bot
from waitress import serve 

# ✅ Load environment variables from Railway
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("CHANNEL_ID")  # Channel ID (starts with -100)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Set OpenAI API key correctly (Fixed)
openai.api_key = OPENAI_API_KEY

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ Initialize Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# ✅ Generate Poll Question Using AI
def generate_poll_question(tweet_text):
    prompt = f"""
    You are a witty AI. Generate a Yes/No poll question based on this tweet:
    "{tweet_text}"
    
    Make it engaging, spicy, tricky, and funny.
    """

    response = openai.ChatCompletion.create(  # ✅ Fixed API call
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content'].strip()

# ✅ Flask Route to Receive Webhook from IFTTT
@app.route('/new_tweet', methods=['POST'])
def new_tweet():
    try:
        data = request.get_json()
        if not data or 'tweet' not in data:
            return jsonify({'error': 'Invalid request'}), 400

        tweet_text = data['tweet']
        print(f"🔹 Received Tweet: {tweet_text}")

        # ✅ Generate AI poll question
        poll_question = generate_poll_question(tweet_text)
        print(f"🔹 Generated Poll: {poll_question}")

        # ✅ Send poll to Telegram channel
        bot.send_poll(
            chat_id=TELEGRAM_CHANNEL_ID,
            question=poll_question,
            options=["Yes", "No"],
            is_anonymous=False
        )

        return jsonify({'status': 'Poll sent successfully'}), 200

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ✅ Run Flask on Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Railway’s assigned port
    serve(app, host="0.0.0.0", port=port)
