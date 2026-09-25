from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

import aiosmtplib
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential

from app.domain.core.config import settings

logger = logging.getLogger(__name__)


def create_verification_code_message(to_: str, verification_code: str) -> MIMEMultipart: 
    message = MIMEMultipart()
    
    message["From"] = settings.SMTP_USER
    message["To"] = to_
    message["Subject"] = "Verification code on WarpFlow"
    
    with open(settings.VERIFICATION_CODE_TEMPLATE_PATH) as file: 
        content = file.read()
        content = content.replace("{url=verification_url}", f"/verification/{verification_code}?email={to_}")
        
    message.attach(MIMEText(content, "html", "utf-8"))
    
    return message


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=3, max=10), 
    retry=retry_if_exception_type(
        (
            aiosmtplib.SMTPConnectError, 
            aiosmtplib.SMTPServerDisconnected, 
            aiosmtplib.SMTPTimeoutError, 
            aiosmtplib.SMTPHeloError
        )
    )
)
async def send_html_message(message: MIMEMultipart) -> None: 
    smtp = aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, use_tls=True, timeout=5.0)
    try:
        await smtp.connect()
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
        await smtp.send_message(message)
    except aiosmtplib.SMTPConnectError as err: 
        logger.error(f"Bad host/port, refused, implicit TLS mismatch: {str(err)}")
        raise
    except aiosmtplib.SMTPServerDisconnected as err: 
        logger.error(f"SMTP server disconnected: {str(err)}")
        raise
    except aiosmtplib.SMTPTimeoutError as err: 
        logger.error(f"SMTP timeout error: {str(err)}")
        raise
    except aiosmtplib.SMTPHeloError as err: 
        logger.error(f"Connect()/start_tls() handshake fail: {str(err)}")
        raise
    except aiosmtplib.SMTPAuthError as err: 
        logger.error(f"Bad user/pass, login before TLS: {str(err)}")
        raise
    except aiosmtplib.SMTPSenderRefused as err: 
        logger.error(f"Missing From/To in MIMEMultipart, rejected address: {str(err)}")
        raise
    except aiosmtplib.SMTPDataError as err: 
        logger.error(f"send_message() — body rejected (size, spam, policy): {str(err)}")
        raise
    except OSError as err: 
        logger.error(f"DNS / network down: {str(err)}")
        raise
    finally:
        if smtp.is_connected:
            await smtp.quit()
    