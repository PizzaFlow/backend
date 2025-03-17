import asyncio

from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema

from app.core.settings import conf


async def send_email(to_email: str, subject: str, body: str):
    html_content = f"""
    <html>
    <body style="background: linear-gradient(135deg, #ff4d00, #ff8800); 
                 padding: 20px; text-align: center; color: white; font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: auto; background: #222; padding: 20px; 
                    border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <h1 style="color: #ffcc00;">PizzaFlow 🍕</h1>
            <p style="font-size: 18px;">{body}</p>
            <hr style="border: 1px solid #ffcc00;">
            <p style="font-size: 14px;">Спасибо, что выбираете нас!</p>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        body=html_content,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

def send_email_background(background_tasks: BackgroundTasks, to_email: str, subject: str, body: str):
    background_tasks.add_task(lambda: asyncio.run(send_email(to_email, subject, body)))
