import smtplib

from django.db import models
from django.contrib.auth.models import User

from_add = 'poisonous1205@gmail.com'
to_addr_list = ['locvx1234@gmail.com']
cc_add_list = []
subject = 'test sent mail'
message = 'minhkma dep trai tu nho'
username = 'poisonous1205@gmail.com'
password = 'minhnguyen'
smtpserver='smtp.gmail.com:587'

class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_alert = models.EmailField(max_length=100, blank=True)
    telegram_id = models.CharField(max_length=10, help_text="Telegram ID", blank=True)
    webhook = models.URLField(help_text="URL to send message into Slack.", blank=True)
    delay_check = models.IntegerField(help_text="unit: minute", default=10)

    def __str__(self):
        return str(self.user)

    class Meta:
        ordering = ('user',)

    def send_email(self, from_add, cc_add_list, subject, 
                    message, password, smtpserver):
        to_addr_list = []
        to_addr_list.append(self.email_alert)
        mes = 'From: {}\nTo: {}\nCc: {}\nSubject: {}\n{}'\
            .format(from_add, ','.join(to_addr_list),
                    ','.join(cc_add_list),
                    subject, message)

        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(from_add, password)
        server.sendmail(from_add, to_addr_list, mes)
        server.quit()




class Host(models.Model):
    hostname = models.CharField(max_length=45)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status_ping = models.IntegerField(default=0)
    status_http = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.hostname) + " (" + str(self.ip_address) + ")" + " - " + str(self.user)

    class Meta:
        ordering = ('hostname',)


class Service(models.Model):
    SERVICE_CHOICES = (
        ('HTTP', 'http'),
        ('PING', 'ping'),
    )
    service_name = models.CharField(max_length=45, choices=SERVICE_CHOICES)
    host = models.ManyToManyField('Host')

    ok = models.IntegerField(help_text="", null=True, blank=True)
    warning = models.IntegerField(help_text="", null=True, blank=True)
    critical = models.IntegerField(help_text="", null=True, blank=True)
    interval_check = models.IntegerField(help_text="", null=True, blank=True, default=20)

    def __str__(self):
        return str(self.service_name)

    class Meta:
        ordering = ('service_name',)
