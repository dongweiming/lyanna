import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

import aiosmtplib
from arq import create_pool, cron
from arq.worker import logger
from mako.lookup import TemplateLookup

from config import (BLOG_URL, MAIL_PASSWORD, MAIL_PORT, MAIL_SERVER,
                    MAIL_USERNAME, REDIS_URL, SITE_TITLE)
from ext import init_db
from models.blog import PAGEVIEW_FIELD, RK_PAGEVIEW, RK_VISITED_POST_IDS, Post
from models.mention import EMAIL_SUBJECT, Mention
from models.utils import RedisSettings

CAN_SEND = all((MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD))


def with_context(f):
    @wraps(f)
    async def _deco(*args, **kwargs):
        await init_db()
        result = await f(*args, **kwargs)
        return result
    return _deco


async def send_email(subject: str, html: str, send_to: str) -> None:
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
        logger.info(f'Send Mail(subject={subject}, html={html}) To {email}')
        await send_email(subject, html.decode(), email)


@with_context
async def flush_to_db(ctx):
    redis = await create_pool(RedisSettings.from_url(REDIS_URL))
    while 1:
        if (post_id := await redis.spop(RK_VISITED_POST_IDS)) is None:
            break

        post = await Post.filter(id=post_id).first()
        if post:
            post._pageview = int(await redis.hget(
                RK_PAGEVIEW.format(post_id), PAGEVIEW_FIELD) or 0)
            await post.save()
            logger.info(f'Flush Post(id={post_id}) pageview')
        else:
            logger.warning(f'Post(id={post_id}) have deleted!')


class WorkerSettings:
    functions = [mention_users]
    cron_jobs = [cron(flush_to_db, hour=None)]
