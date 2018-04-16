from django.db import models
from django.contrib.auth.models import User


class Alert(models.Model):
    service = models.OneToOneField('Service', on_delete=models.CASCADE, primary_key=True,)
    email_alert = models.EmailField(max_length=100, blank=True)
    telegram_id = models.CharField(max_length=10, help_text="Telegram ID", blank=True)
    webhook = models.URLField(help_text="URL to send message into Slack.", blank=True)

    def __str__(self):
        return str(self.service)

    class Meta:
        ordering = ('service',)


class Host(models.Model):
    hostname = models.CharField(max_length=45)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

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

    ok = models.IntegerField(help_text="", blank=True)
    warning = models.IntegerField(help_text="", blank=True)
    critical = models.IntegerField(help_text="", blank=True)
    interval_check = models.DurationField()

    def __str__(self):
        return str(self.service_name)

    class Meta:
        ordering = ('service_name',)
