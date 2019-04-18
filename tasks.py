import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from contextlib import asynccontextmanager
except ModuleNotFoundError:
    from async_generator import asynccontextmanager

from aiotasks import build_manager

from ext import init_db, mako
from models.blog import Post
from models.mention import Mention, EMAIL_SUBJECT, EMAIL_BODY
from config import (MAIL_SERVER, MAIL_PORT, MAIL_USERNAME,
                    MAIL_PASSWORD, REDIS_URL, SITE_TITLE)

manager = build_manager(REDIS_URL)
CAN_SEND = all((MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD))


@manager.task()
async def send_email(subject, content, send_to):
    if not CAN_SEND:
        return

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = MAIL_USERNAME
    msg['To'] = send_to
    msg.attach(MIMEText(message, 'html'))

    s = smtplib.SMTP_SSL(MAIL_SERVER, port=MAIL_PORT)
    s.login(MAIL_USERNAME, MAIL_PASSWORD)
    if not isinstance(send_to, list):
        send_to = [send_to]
    s.send_message(msg)
    s.quit()


@manager.task()
async def mention_users(post_id, content, author_id):
    await init_db()
    post = await Post.cache(post_id)
    if not post:
        return
    mention_users = await Mention.get_mention_users(content, author_id)
    for user in mention_users:
        email = user.email
        if not email:
            continue
        subject = EMAIL_SUBJECT.format(title=post.title)
        content = EMAIL_BODY.format(site=SITE_TITLE, subject=post.title,
                                    name=user.username)
        await send_email.delay(subject, content, email)
