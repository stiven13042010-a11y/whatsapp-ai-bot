import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client # הוספנו את מנהל השליחה היזומה
import google.generativeai as genai

# משיכת המפתחות מהסביבה (Render)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# הגדרת פרטי ההתחברות לטוויליו לשליחה יזומה
twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_auth = os.environ.get("TWILIO_AUTH_TOKEN")
# אתחול הקליינט של טוויליו (רק אם המפתחות קיימים)
twilio_client = Client(twilio_sid, twilio_auth) if twilio_sid and twilio_auth else None

# הגדרת המודל
model = genai.GenerativeModel('gemini-2.5-flash')
app = Flask(__name__)

# --- הנתיב החדש: קליטת ליד מ-Make ויזימת שיחה ---
@app.route('/new-lead', methods=['POST'])
def handle_new_lead():
    try:
        # 1. קבלת הנתונים מ-Make
        data = request.json
        lead_name = data.get('name', 'לקוח/ה')
        lead_phone = str(data.get('phone', ''))

        # סידור מספר הטלפון: אם הלקוחה השאירה 050, נהפוך ל-97250 כדי שטוויליו יבין
        if lead_phone.startswith('0'):
            lead_phone = '972' + lead_phone[1:]
        
        # 2. ניסוח ההודעה הפרואקטיבית (יוזמת)
        first_message = f"היי {lead_name}, ראיתי שהשארת פרטים לגבי צילומים בסטודיו בראשית! איריס כרגע על הסט, אני העוזר הווירטואלי שלה. מתי האירוע שלכם?"

        # 3. שליחת ההודעה דרך טוויליו
        if twilio_client:
            twilio_client.messages.create(
                from_='whatsapp:+14155238886', # המספר האמריקאי של הבוט
                to=f'whatsapp:+{lead_phone}',
                body=first_message
            )
            print(f"✅ Successfully sent first message to lead: {lead_name}")
            return "Lead processed!", 200
        else:
            print("❌ Twilio credentials not found in environment variables.")
            return "Twilio Config Error", 500

    except Exception as e:
        print(f"❌ Error processing lead: {e}")
        return "Error", 500


# --- הנתיב הרגיל: תגובה להודעות נכנסות ---
@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '')
    sender_phone = request.values.get('From', '')

    # --- הניתוב החכם (Routing) ---
    if sender_phone == 'whatsapp:+972509797651': 
        bot_persona = """אתה העוזר הווירטואלי החכם של קליניקת הקוסמטיקה והאסתטיקה המתקדמת בניהולה של לימור.

המטרה שלך:
לתת מענה אדיב, מקצועי ואישי למתעניינות, לענות על שאלות בסיסיות, והכי חשוב - לאסוף פרטים ולהוביל אותן לקביעת פגישת אבחון עור בקליניקה.

תחומי ההתמחות של הקליניקה של לימור:
1. טיפולי אקנה (ריפוי פצעים, טיפול בצלקות פוסט-אקנה, ואיזון העור).
2. מיצוק העור (החזרת הגמישות, טיפולי זוהר וגלאם).
3. אנטי אייג'ינג (הצערת העור, טשטוש קמטים וחידוש המרקם).

טון וסגנון דיבור:
- רך, סבלני, מכיל ומרגיע. אנשים שמגיעים לטיפולי עור (במיוחד אקנה) לפעמים חסרי ביטחון, תן להם תחושה שהם בידיים הכי מקצועיות שיש.
- קצר, זורם ובגובה העיניים. אתה מדבר בוואטסאפ, אל תכתוב פסקאות ארוכות מדי.
- השתמש באימוג'ים עדינים שקשורים לטיפוח ורוגע (כמו ✨, 🌿, 💆‍♀️, 🤍) אבל במידה.

כללי ברזל (חובה לציית להם):
1. אל תיתן ייעוץ רפואי ואל תמליץ על תרופות. אתה יכול להמליץ רק על שגרת טיפוח כללית.
2. ניווט השיחה: תמיד תסיים הודעות בשאלה שמקדמת את השיחה. למשל: "ממה את הכי סובלת כרגע בעור?", "מה שגרת הטיפוח הנוכחית שלך?", או "תרצי שנתאם פגישת אבחון עם לימור?"
3. התנגדות מחיר: אם שואלים כמה עולה טיפול, אל תזרוק מספרים. תסביר בעדינות שכל טיפול מותאם אישית למצב העור, ולכן המחיר המדויק נקבע רק לאחר אבחון מקצועי בקליניקה על ידי לימור."""
    else:
        # הפרומפט של איריס
        bot_persona = """אתה עוזר וירטואלי של סטודיו בראשית. הסטודיו מתמחה בצילומי פורטרטים ואמנות. 
        המטרה שלך היא לתת שירות אדיב, לענות על שאלות בנוגע לצילומים, להסביר על סגנון הצילום הטבעי, ולאסוף פרטים כמו תאריך האירוע ומיקום."""

    # חיבור הפרומפט של הבוט יחד עם ההודעה של הלקוח
    full_prompt = f"{bot_persona}\n\nהודעת הלקוח/ה: {incoming_msg}\nתשובתך:"

    try:
        # שליחה לג'מיני
        response = model.generate_content(full_prompt)
        ai_answer = response.text
    except Exception as e:
        ai_answer = "סליחה, יש לי כרגע עומס קטן במערכת. אשמח אם תשלחו את ההודעה שוב בעוד דקה."
        print(f"Error: {e}")

    # החזרת התשובה לטוויליו
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(ai_answer)

    return str(resp)

if __name__ == '__main__':
    app.run(port=5000, debug=True)