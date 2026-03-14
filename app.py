from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import os

# הגדרת ה-AI
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# יצירת אובייקט שיחה גלובלי עם ההוראות של הבוט
chat = model.start_chat(history=[
    {"role": "user", "parts": ["אתה נציג שירות של 'פיצה סטיבן'. תפריט: משפחתית 50, אישית 30, תוספות 5. שעות: 10:00-22:00. תענה קצר ובעברית, ותזכור את פרטי ההזמנה של הלקוח."]},
    {"role": "model", "parts": ["שלום! אני הנציג של פיצה סטיבן. איך אוכל לעזור לכם היום?"]}
])

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '')
    
    # שליחת ההודעה לתוך ה-session הקיים של הצ'אט
    response = chat.send_message(incoming_msg)
    ai_answer = response.text

    # החזרת התשובה לוואטסאפ
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(ai_answer)

    return str(resp)

if __name__ == '__main__':
    app.run(port=5000, debug=True)