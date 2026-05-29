import csv, io, json, anthropic
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "вставь_токен"
ANTHROPIC_KEY = "вставь_ключ"

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Напиши: тату салоны Москва")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    await update.message.reply_text(f"🔍 Ищу: {text}...")
    try:
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            system='Только JSON: {"businesses":[{"name":"...","address":"...","rating":4.5,"phone":"...","website":"... или null","email":"... или null","instagram":"... или null","vk":"... или null","telegram":"... или null"}]}. Генерируй 8-10 заведений.',
            messages=[{"role":"user","content":text}]
        )
        data = json.loads(r.content[0].text)
        businesses = data["businesses"]
        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=["name","address","rating","phone","website","email","instagram","vk","telegram"])
        w.writeheader()
        w.writerows(businesses)
        buf = io.BytesIO(out.getvalue().encode("utf-8-sig"))
        msg = f"✅ Найдено: {len(businesses)}\n\n"
        for b in businesses[:5]:
            msg += f"• {b['name']} | {b['phone']}\n"
        await update.message.reply_text(msg)
        await update.message.reply_document(document=buf, filename=text.replace(" ","_")+".csv", caption="📁 База контактов")
    except Exception as e:
        await update.message.reply_text(f"❌ {str(e)}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
print("Бот запущен!")
app.run_polling()
