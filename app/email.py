"""Transactional email (invite / password reset) via SMTP — optional.

If SMTP isn't configured (``settings.email_enabled`` is False), sends are no-ops
that return ``False``; the admin UI then surfaces the link to share manually.
"""

from __future__ import annotations

import logging
from email.message import EmailMessage

import aiosmtplib

from .config import settings

log = logging.getLogger("bluchip.email")


async def _send(to: str, subject: str, body: str) -> bool:
    if not settings.email_enabled:
        return False
    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=settings.SMTP_STARTTLS,
        )
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("email send to %s failed: %s", to, exc)
        return False


async def send_invite(to: str, full_name: str, link: str) -> bool:
    name = full_name or "there"
    body = (
        f"Hi {name},\n\n"
        "You've been invited to BluChip Agent-Assist. Click the link below to set "
        "your password and activate your account:\n\n"
        f"{link}\n\n"
        f"This link expires in {settings.INVITE_TOKEN_TTL_HOURS} hours.\n"
    )
    return await _send(to, "Your BluChip Agent-Assist invitation", body)


async def send_reset(to: str, link: str) -> bool:
    body = (
        "Hi,\n\n"
        "We received a request to reset your BluChip Agent-Assist password. Click "
        "the link below to choose a new one:\n\n"
        f"{link}\n\n"
        f"This link expires in {settings.RESET_TOKEN_TTL_HOURS} hours. If you didn't "
        "request this, you can ignore this email.\n"
    )
    return await _send(to, "Reset your BluChip Agent-Assist password", body)
