import asyncio
import datetime
import os
import nest_asyncio
from telegram import Update  # type: ignore
from telegram.ext import Application, CommandHandler  # type: ignore
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib  # type: ignore

# Getting HTML file for message. 
def generate_receipt(amount=1000, qty=None):
    if qty is None: #Variable
        qty = "1"
    
    template_path = "receipt_template.html"
    
    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()
    return template.replace("{{amount}}", str(amount)).replace("{{qty}}", qty) #1&2 Variable

# Sending message
async def send_email(receipt_html, to_email):
    from_email = "EMAIL_SENDER"
    password = "EMAIL_PASSWORD"
    smtp_host = "smtp.gmail.com"
    smtp_port = 587

    if not from_email or not password:
        print("Error: email has not found.")
        return False

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Ваш чек"
    msg.attach(MIMEText(receipt_html, 'html'))

    try:
        smtp_client = aiosmtplib.SMTP()
        await smtp_client.connect(hostname=smtp_host, port=smtp_port, start_tls=True)
        await smtp_client.login(from_email, password)
        await smtp_client.send_message(msg)
        await smtp_client.quit()
        return True
    except Exception as e:
        print(f"Error with sending email: {e}")
        return False

# Command for send message
async def send_receipt(update: Update, context):
    if not context.args:
        await update.message.reply_text("Please, set email after command. Example: /send_receipt email@example.com 1500 2")
        return

    user_email = context.args[0]
    amount = context.args[1] if len(context.args) > 1 else "1000" # Variable
    qty = context.args[2] if len(context.args) > 2 else "1"# Variable
    receipt_html = generate_receipt(amount, qty)# 1&2 Variables in html files
    success = await send_email(receipt_html, user_email)

    if success:
        await update.message.reply_text("Message has been sent!")
    else:
        await update.message.reply_text("Error with sending.")


# Start bot
async def main():
    bot_token = "YOUR_BOT_API_TOKEN"
    if not bot_token:
        print("Error: not found TELEGRAM_BOT_TOKEN")
        return

    app = Application.builder().token(bot_token).build()

    # Add command /send_receipt
    app.add_handler(CommandHandler("send_receipt", send_receipt))

    print("Bot is runnig!")
    await app.run_polling(allowed_updates=Update.ALL_TYPES)



# Запуск бота
if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
