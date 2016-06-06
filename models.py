from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.
class AccountModel(models.Model):
    return_address = models.CharField(verbose_name='Return Address:', max_length=34, blank=False, null=False, editable=True)
    checked = models.IntegerField(default=0, editable=False)
    balance = models.DecimalField(default=0, max_digits=16, decimal_places=8, editable=False, validators=[MaxValueValidator(21000000)])
    created = models.DateTimeField(auto_now_add=True, editable=False)

class ArchiveModel(models.Model):
    return_address = models.CharField(max_length=34, blank=False, null=False, editable=False)
    checked = models.IntegerField(editable=False)
    balance = models.DecimalField(max_digits=16, decimal_places=8, editable=False, validators=[MaxValueValidator(21000000)])
    created = models.DateTimeField(editable=False)

class BrokenModel(models.Model):
    return_address = models.CharField(max_length=34, blank=False, null=False, editable=False)
    checked = models.IntegerField(editable=False)
    balance = models.DecimalField(max_digits=16, decimal_places=8, editable=False, validators=[MaxValueValidator(21000000)])
    created = models.DateTimeField(editable=False)

class InvalidModel(models.Model):
    return_address = models.CharField(max_length=34, blank=False, null=False, editable=False)
    checked = models.IntegerField(editable=False)
    balance = models.DecimalField(max_digits=16, decimal_places=8, editable=False, validators=[MaxValueValidator(21000000)])
    created = models.DateTimeField(editable=False)

class ResultModel(models.Model):
    winning_address = models.CharField(verbose_name="Winning Address", max_length=34, null=False, blank=False)
    winning_deposit = models.CharField(verbose_name="Winning Deposit", max_length=17, null=False, blank=False)
    losing_deposit = models.CharField(verbose_name="Losing Deposit", max_length=17, null=False, blank=False)
    losing_address = models.CharField(verbose_name="Losing Address", max_length=34, null=False, blank=False)
    txid = models.CharField(verbose_name="Txid", max_length=64, null=False, blank=False)
    # winning_output_transaction_hash_db = models.CharField(max_length=64, null=False, blank=False)
    # losing_output_transaction_hash_db = models.CharField(max_length=64, null=False, blank=False)
