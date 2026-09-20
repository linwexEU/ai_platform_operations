import asyncio

from app.infrastructure.worker.celery import app
from app.infrastructure.email.smtp_email import create_verification_code_message, send_html_message


async def send_verification_code(code: str, email: str) -> None: 
    message = create_verification_code_message(email, code)
    await send_html_message(message)
    

@app.task()
def task_send_verification_code(code: str, email: str) -> None: 
    asyncio.run(send_verification_code(code, email))
