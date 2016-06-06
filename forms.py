__author__ = 'derrend'
from django import forms
from captcha.fields import CaptchaField
from models import AccountModel

class AccountForm(forms.ModelForm):
    class Meta:
        model = AccountModel
        fields = "__all__"
    # refund_address = forms.CharField(label='Return Address',max_length=35)
    # checked = forms.IntegerField(label='Checked')

class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()

class ResultsSearchForm(forms.Form):
    search = forms.CharField(label='Search ID, Address, Amount or Txid')
