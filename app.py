from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import os

# הגדרת ה-AI
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# יצירת אובייקט שיחה גלובלי עם ההוראות של הבוט
# יצירת אובייקט שיחה גלובלי עם ההוראות של הבוט
# יצירת אובייקט שיחה גלובלי עם ההוראות של הבוט לקוסמטיקאית
chat = model.start_chat(history=[
    {"role": "user", "parts": ["אתה נציג שירות וירטואלי אדיב, נשי ומקצועי של 'שירה קוסמטיקה' ברמת גן (רחוב בית לחם 4). המטרה שלך היא לענות ללקוחות שפונות בוואטסאפ, לתת להן מידע על טיפולים, ולעזור להן. שעות פעילות: א'-ה' 09:00-18:00. טיפולים: טיפול פנים קלאסי (250 ש\"ח), סידור גבות (50 ש\"ח), פדיקור רפואי (120 ש\"ח). תענה תמיד בעברית, בצורה חמה ומזמינה, קצר ולעניין."]},
    {"role": "model", "parts": ["היי! הגעת לשירה קוסמטיקה. איזה כיף שפנית אליי, איך אפשר לפנק אותך היום?"]}
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