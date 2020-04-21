import urllib

import certifi
from urllib3 import Retry

from healthybank.celery import app

import os
import json

from django.conf import settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(queue='low_priority')
def send_email(**kwargs):
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email='no-reply@wellmoapp.in',
        to_emails=kwargs.get('to_emails'),
        subject=kwargs['subject'] if 'subject' in kwargs else ''
    )
    message.dynamic_template_data = kwargs
    message.template_id = settings.SENDGRID_TEMPLATES[kwargs['template']]
    SENDGRID_API_KEY = settings.SENDGRID_API_KEY
    try:
        sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        logger.exception(e)
    return


@app.task(queue='low_priority')
def sent_mobile_otp(**kwargs):
    print(kwargs)
    message = Mail(
        from_email='no-reply@wellmoapp.in',
        to_emails=kwargs.get('to_emails'),
        subject=kwargs['subject'] if 'subject' in kwargs else ''
    )
    message.dynamic_template_data = kwargs
    message.template_id = settings.SENDGRID_TEMPLATES[kwargs['template']]
    SENDGRID_API_KEY = settings.SENDGRID_API_KEY
    try:
        sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
    return


@app.task(queue='low_priority', bind=True, default_retry_delay=30)
def sent_mobile_sms(self, **kwargs):
    values = {'authkey': settings.MSG91_AUTH_KEY,
              'mobiles': '91' + kwargs['mobile'],
              'message': kwargs['message'],
              'sender': settings.MSG91_SENDER,
              'route': 4,
              'country': 91
              }

    url = "https://api.msg91.com/api/sendhttp.php"  # API URL
    import urllib3
    queryparams = urllib.parse.urlencode(values)  # URL encoding the data here.
    retries = Retry(connect=5, read=2, redirect=5, backoff_factor=1)
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where(), retries=retries)

    req = http.request('GET', url + '?' + queryparams)

    if req.status == 200:
        logger.debug("Data Received %s " % req.data)  # Get Response
        return
    else:
        raise
        logger.error("Error from msg91 %s " % req.status)
