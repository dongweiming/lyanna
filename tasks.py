import asyncio
from functools import wraps
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from mako.lookup import TemplateLookup

from ext import init_db
from models.blog import Post
from models.mention import Mention, EMAIL_SUBJECT
from config import (MAIL_SERVER, MAIL_PORT, MAIL_USERNAME,
                    MAIL_PASSWORD, SITE_TITLE, BLOG_URL)

CAN_SEND = all((MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD))


def with_context(f):
    @wraps(f)
    async def _deco(*args, **kwargs):
        await init_db()
        result = await f(*args, **kwargs)
        return result
    return _deco


async def send_email(subject, html, send_to):
    if not CAN_SEND:
        return

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = MAIL_USERNAME
    msg['To'] = send_to
    msg.attach(MIMEText(html, 'html'))

    loop = asyncio.get_event_loop()
    smtp = aiosmtplib.SMTP(hostname=MAIL_SERVER, port=MAIL_PORT,
                           loop=loop, use_tls=True)
    await smtp.connect()
    await smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
    await smtp.send_message(msg)
    await smtp.quit()


@with_context
async def mention_users(ctx, post_id, content, author_id):
    post = await Post.cache(post_id)
    if not post:
        return
    mention_users = await Mention.get_mention_users(content, author_id)
    for user in mention_users:
        email = user.email
        if not email:
            continue
        subject = EMAIL_SUBJECT.format(title=post.title)
        lookup = TemplateLookup(directories=['templates'],
                                input_encoding='utf-8',
                                output_encoding='utf-8')
        template = lookup.get_template('email/mention.html')
        html = template.render(username=user.username,
                               site_url=BLOG_URL, post=post,
                               site_name=SITE_TITLE)
        await send_email(subject, html.decode(), email)


class WorkerSettings:
    functions = [mention_users]
