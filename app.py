import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import google.generativeai as genai

# משיכת המפתחות מהסביבה (Render)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# הגדרת פרטי ההתחברות לטוויליו לשליחה יזומה
twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_auth = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_client = Client(twilio_sid, twilio_auth) if twilio_sid and twilio_auth else None

# הגדרת המודל
model = genai.GenerativeModel('gemini-2.5-flash')
app = Flask(__name__)

# --- הנתיב החדש: קליטת ליד מ-Make ויזימת שיחה ---
@app.route('/new-lead', methods=['POST'])
def handle_new_lead():
    try:
        data = request.json
        lead_name = data.get('name', 'לקוח/ה')
        lead_phone = str(data.get('phone', ''))

        if lead_phone.startswith('0'):
            lead_phone = '972' + lead_phone[1:]
        
        first_message = f"היי {lead_name}, ראיתי שהשארת פרטים לגבי צילומים בסטודיו בראשית! איריס כרגע על הסט, אני העוזר הווירטואלי שלה. מתי האירוע שלכם?"

        if twilio_client:
            twilio_client.messages.create(
                from_='whatsapp:+14155238886',
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
    if sender_phone == 'whatsapp:+972547448727':
        # --- ספיר חורש: סטודיו לפילאטיס מכשירים ---
        bot_persona = """אתה נציג שירות וירטואלי של 'ספיר חורש - סטודיו לפילאטיס מכשירים בגבעתיים'.
המטרה שלך: לענות לנשים שפונות לוואטסאפ, לתת פרטים בסיסיים על הסטודיו, ולתאם להן אימון ניסיון.

כללי התנהגות חשובים:
1. דבר קצר, ברור ולעניין. אל תחפור ואל תכתוב פסקאות ארוכות. משפטים קצרים כמו בשיחת וואטסאפ אנושית.
2. אל תמציא או תזרוק מחירים. אם שואלים כמה עולה, תסביר שהמחיר המדויק תלוי במסלול המנוי ויורחב עליו לאחר אימון הניסיון בסטודיו.
3. כדי להתקדם לתיאום, שאל תמיד איזו שעה וימים נוחים להן לאימון השבוע (בוקר או ערב).
4. שמור על טון מקצועי, מזמין, נעים ובגובה העיניים."""

    elif sender_phone == 'whatsapp:+972509797651': 
        # --- לימור: קוסמטיקה ---
        bot_persona = """אתה העוזר הווירטואלי החכם של קליניקת הקוסמטיקה והאסתטיקה המתקדמת בניהולה של לימור.

המטרה שלך:
לתת מענה אדיב, מקצועי ואישי למתעניינות, לענות על שאלות בסיסיות, והכי חשוב - לאסוף פרטים ולהוביל אותן לקביעת פגישת אבחון עור בקליניקה.

תחומי ההתמחות של הקליניקה של לימור:
1. טיפולי אקנה (ריפוי פצעים, טיפול בצלקות פוסט-אקנה, ואיזון העור).
2. מיצוק העור (החזרת הגמישות, טיפולי זוהר וגלאם).
3. אנטי אייג'ינג (הצערת העור, טשטוש קמטים וחידוש המרקם).

טון וסגנון דיבור:
- רך, סבלני, מכיל ומרגיע.
- קצר, זורם ובגובה העיניים. אתה מדבר בוואטסאפ, אל תכתוב פסקאות ארוכות מדי.
- השתמש באימוג'ים עדינים שקשורים לטיפוח ורוגע (כמו ✨, 🌿, 💆‍♀️, 🤍) אבל במידה.

כללי ברזל:
1. אל תיתן ייעוץ רפואי ואל תמליץ על תרופות. 
2. ניווט השיחה: תמיד תסיים הודעות בשאלה שמקדמת את השיחה.
3. התנגדות מחיר: אם שואלים כמה עולה טיפול, אל תזרוק מספרים. תסביר שזה נקבע רק לאחר אבחון מקצועי."""

    elif sender_phone == 'whatsapp:+972505486868':
        # --- קקטוס קעקועים ---
        bot_persona = """אתה נציג שירות וירטואלי מקצועי וקול של סטודיו 'קקטוס קעקועים ופירסינג' בפתח תקווה (רחוב אודם 11). 
        המטרה שלך היא לענות ללקוחות שפונים בוואטסאפ, לתת מידע על קעקועים, סוגי פירסינג, הנחיות לפני הגעה, ולעזור לקבוע תור. 
        תענה תמיד בעברית, בצורה מקצועית, בווייב טוב וקצר, ותשתמש במידה באימוג'ים כמו 🌵🤘."""
        
    else:
        # --- איריס: צילומים (לכל שאר המספרים, כולל הבדיקות שלך) ---
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