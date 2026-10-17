"""Sending email through SMTP (Gmail for now).

Settings come from .env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM.
Used by the document "Email" button and, later, hearing reminders.
"""
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import settings

# Gmail refuses emails over ~25 MB, and attachments grow ~33% when emailed,
# so files bigger than this can't be sent.
MAX_ATTACHMENT_BYTES = 18 * 1024 * 1024


class EmailNotConfigured(RuntimeError):
    """SMTP settings are missing in .env."""


def email_enabled() -> bool:
    return bool(settings.SMTP_USER and settings.SMTP_PASSWORD)


def build_message(
    *,
    to: str,
    subject: str,
    body: str,
    from_name: str,
    reply_to: str | None = None,
    attachment: tuple[str, bytes, str] | None = None,
) -> EmailMessage:
    """Build the email. attachment = (filename, file_bytes, content_type)."""
    msg = EmailMessage()
    msg["From"] = formataddr((from_name, settings.EMAIL_FROM or settings.SMTP_USER))
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)

    if attachment:
        filename, content, content_type = attachment
        maintype, _, subtype = content_type.partition("/")
        msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)
    return msg


def send_message(msg: EmailMessage) -> None:
    """Log in to the SMTP server (encrypted) and send the email."""
    if not email_enabled():
        raise EmailNotConfigured("Email is not set up: add SMTP_USER and SMTP_PASSWORD to .env")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)