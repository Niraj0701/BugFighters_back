import boto3

from healthybank.celery import app
from commons.tasks import send_email, sent_mobile_otp, sent_mobile_sms
from django.conf import settings
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(queue='low_priority')
def otp_generated(**kwargs):
    logger.debug("Evaluating otp generation")
    if 'otp' in kwargs and kwargs['otp'] is not None:
        subject =  "%s is your otp for Shopping Token account " % kwargs['otp']
        if 'email' in kwargs and kwargs['email'] is not None:

            send_email.delay(to_emails=kwargs['email'], otp=kwargs['otp'], subject=subject,
                             template='OTP_GENERATED')
        if 'mobile' in kwargs and kwargs['mobile'] is not None:
            logger.debug("Sending otp here %s %s " % (kwargs['otp'], kwargs['mobile']))
            sent_mobile_sms.apply_async(
                kwargs={'mobile': '+' + kwargs['country_code']+kwargs['mobile'], 'message': subject })
