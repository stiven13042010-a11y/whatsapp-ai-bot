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
    {"role": "user", "parts": ["אתה נציג שירות וירטואלי מקצועי, אדיב ודיסקרטי של מרפאת האסתטיקה של 'ד''ר יניב ביגו' ברמת החייל, תל אביב (הברזל 15). המטרה שלך היא לענות ללקוחות שפונות בוואטסאפ, לספק מידע על טיפולים אסתטיים (הזרקות, פיסול פנים, טיפולי עור), ולסייע בתיאום תורי ייעוץ לקליניקה. תענה תמיד בעברית, בשפה גבוהה, מרגיעה ומכבדת."]},
    {"role": "model", "parts": ["שלום, הגעת לקליניקה לאסתטיקה של ד\"ר יניב ביגו. איך אוכל לעזור לך היום? ✨"]}
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