import logging
import random
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
nest_asyncio.apply()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- QUESTIONS DATABASE ---
QUESTIONS = [
        {"q": "67. من هو الشاعر الأردني المعروف بلقب 'عرار'؟", "options": ["حبيب الزيودي", "مصطفى وهبي التل", "تيسير السبول", "عرار النابلسي"], "correct": 1},
    {"q": "68. من هو الطبيب والمفكر الأردني الذي أسّس الجامعة الأردنية؟", "options": ["وصفي التل", "هزاع المجالي", "عبد السلام المجالي", "فوزي الملقي"], "correct": 2},
    {"q": "69. من هو الشاعر الأردني الذي كتب كلمات النشيد الوطني 'عاش المليك'؟", "options": ["إبراهيم طوقان", "عبد المنعم الرفاعي", "حيدر محمود", "سعيد عقل"], "correct": 1},
    {"q": "70. من هو الفنان الأردني الذي يُعتبر من رواد الدراما البدوية؟", "options": ["زهير النوباني", "ياسر المصري", "جميل عواد", "روحي الصفدي"], "correct": 1},
    {"q": "71. من هو أول طيار أردني استشهد في حرب 1948؟", "options": ["فراس العجلوني", "موفق السلطي", "معاذ الكساسبة", "كاسب صفوق"], "correct": 0},
    {"q": "72. من هو الرياضي الأردني الذي حقق أول ميدالية أولمبية للأردن في التايكواندو؟", "options": ["صالح الشرباتي", "جوليانا الصادق", "أحمد أبو غوش", "محمد أبو لبدة"], "correct": 2},
    {"q": "73. من هو أبرز لاعب أردني برز اسمه في الدوري الفرنسي مؤخراً؟", "options": ["يزن النعيمات", "موسى التعمري", "محمود المرضي", "عامر شفيع"], "correct": 1},
    {"q": "74. من هو اللاعب الأردني الوحيد الذي لعب لريال مدريد وبرشلونة؟", "options": ["عدي الصيفي", "حمزة الدردور", "ثائر البواب", "عبدالله ذيب"], "correct": 2},
    {"q": "75. من هو الملك الأردني الذي لُقّب بـ 'الباني'؟", "options": ["الملك عبدالله الأول", "الملك طلال", "الملك حسين بن طلال", "الملك عبدالله الثاني"], "correct": 2},
    {"q": "76. من هي أول رائدة فضاء أردنية؟", "options": ["رنا الدجاني", "سلام أبو الهيجاء", "لانا مامكغ", "تغريد حكمت"], "correct": 1},
    {"q": "77. من هو أغنى رجل أعمال أردني؟", "options": ["صبيح المصري", "طلال أبو غزالة", "زياد المناصير", "حمدي الطباع"], "correct": 2},
    {"q": "78. ما اسم القائد المسلم المدفون في المزار الجنوبي مع جعفر بن أبي طالب؟", "options": ["خالد بن الوليد", "زيد بن حارثة وعبد الله بن رواحة", "عمرو بن العاص", "عكرمة بن أبي جهل"], "correct": 1},
    {"q": "79. في أي مدينة أردنية توجد أضرحة شهداء معركة مؤتة؟", "options": ["غور الصافي", "المزار الجنوبي في الكرك", "دير علا", "الشونة الشمالية"], "correct": 1},
    {"q": "80. ما اسم الصحابي القائد المدفون في غور الأردن وكان أمين الأمة؟", "options": ["معاذ بن جبل", "أبو عبيدة عامر بن الجراح", "ضرار بن الأزور", "شرحبيل بن حسنة"], "correct": 1},
    {"q": "81. ما اسم القائد المسلم المدفون في المزار الجنوبي مع جعفر بن أبي طالب؟ (تكرار)", "options": ["شرحبيل بن حسنة", "زيد بن حارثة وعبد الله بن رواحة", "عبادة بن الصامت", "بلال بن رباح"], "correct": 1},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"مرحباً بك {user_name} في مسابقة شخصيات الأردنّ 🇯🇴\n\n"
        "اضغط /quiz للبدء باختبار معلوماتك!"
    )

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Pick a random question from the entire list
    random_idx = random.randint(0, len(QUESTIONS) - 1)
    q_data = QUESTIONS[random_idx]
    
    context.user_data['current_q_idx'] = random_idx

    # Create buttons for options
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{i}")] for i, opt in enumerate(q_data['options'])]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"سؤال الشخصيات:\n\n{q_data['q']}"
    
    # If called from a button, edit the message; if from /quiz, send new
    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("ans_"):
        selected = int(data.replace("ans_", ""))
        q_idx = context.user_data.get('current_q_idx')
        
        correct = QUESTIONS[q_idx]['correct']
        
        if selected == correct:
            result_text = "✅ إجابة صحيحة! أحسنت."
        else:
            ans_text = QUESTIONS[q_idx]['options'][correct]
            result_text = f"❌ إجابة خاطئة.\nالصحيح هو: {ans_text}"

        # Show result and button for next question
        keyboard = [[InlineKeyboardButton("سؤال آخر 🔄", callback_data="next_question")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"السؤال: {QUESTIONS[q_idx]['q']}\n\n{result_text}",
            reply_markup=reply_markup
        )

    elif data == "next_question":
        await send_question(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", send_question))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("البوت يعمل الآن... جرب إرسال /quiz")
    app.run_polling(close_loop=False)

if __name__ == '__main__':
    main()
