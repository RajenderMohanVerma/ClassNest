"""Outbound email for account verification and password reset.

Delivery is opt-in: without ``MAIL_ENABLED`` and a server, nothing is sent and
the caller is told so. That keeps an unconfigured deployment honest instead of
pretending an email went out.

Tokens are never placed in the subject line, because mail subjects show up in
mailbox list views and notification previews.
"""

import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from flask import current_app

logger = logging.getLogger(__name__)

# Sent as the envelope sender when MAIL_FROM is not set.
FALLBACK_FROM = 'no-reply@localhost'


def is_configured():
    """True when a real mail transport is configured."""
    config = current_app.config
    return bool(
        config.get('MAIL_ENABLED')
        and config.get('MAIL_SERVER')
        and config.get('MAIL_FROM')
    )


def send_email(recipient, subject, body):
    """Send one plain-text email. Returns ``True`` only on real delivery.

    Never raises: a mail outage must not turn a working password reset into a
    500. Failures are logged and reported as ``False`` so the route can show
    an honest message.
    """
    if not recipient or '@' not in recipient:
        return False

    if not is_configured():
        logger.warning(
            'MAIL_ENABLED/MAIL_SERVER/MAIL_FROM are not configured; '
            'skipped email to %s (subject: %s)', recipient, subject,
        )
        return False

    config = current_app.config
    sender = config['MAIL_FROM']
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = formataddr((current_app.config['APP_NAME'], sender))
    message['To'] = recipient
    message.set_content(body)

    try:
        with smtplib.SMTP(
            config['MAIL_SERVER'],
            config['MAIL_PORT'],
            timeout=15,
        ) as smtp:
            if config.get('MAIL_USE_TLS'):
                smtp.starttls()
            if config.get('MAIL_USERNAME'):
                smtp.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        logger.exception(
            'Failed to send email to %s via %s: %s',
            recipient, config['MAIL_SERVER'], exc,
        )
        return False

    logger.info('Sent "%s" to %s', subject, recipient)
    return True


def send_verification_email(recipient, name, link):
    return send_email(
        recipient,
        f'Verify your {current_app.config["APP_NAME"]} email address',
        _verification_body(name, link),
    )


def send_password_reset_email(recipient, name, link):
    return send_email(
        recipient,
        f'Reset your {current_app.config["APP_NAME"]} password',
        _reset_body(name, link),
    )


def _verification_body(name, link):
    minutes = current_app.config.get('PASSWORD_RESET_TTL_MINUTES', 30)
    return (
        f'Hello {name},\n\n'
        f'Confirm this email address for your {current_app.config["APP_NAME"]} '
        f'account:\n\n'
        f'{link}\n\n'
        f'The link works once and expires in {minutes} minutes. '
        f'If you did not create this account, ignore this email.\n'
    )


def _reset_body(name, link):
    minutes = current_app.config.get('PASSWORD_RESET_TTL_MINUTES', 30)
    return (
        f'Hello {name},\n\n'
        f'Use the link below to choose a new password for your '
        f'{current_app.config["APP_NAME"]} account:\n\n'
        f'{link}\n\n'
        f'The link works once and expires in {minutes} minutes. '
        f'If you did not ask for this, no change has been made and you can '
        f'ignore this email.\n'
    )