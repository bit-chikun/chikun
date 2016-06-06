from __future__ import print_function

from django.shortcuts import render, render_to_response, HttpResponse, redirect
from django.template.context_processors import csrf
from tables import ResultsTable #, FilterForm
from models import AccountModel, ArchiveModel, BrokenModel, InvalidModel, ResultModel
from forms import CaptchaTestForm, AccountForm, ResultsSearchForm
from django_tables2 import RequestConfig
from django.views.decorators.csrf import csrf_exempt

from blockchain.exchangerates import get_ticker     # remote
from blockchain.blockexplorer import get_address    # remote
from blockchain.pushtx import pushtx                # remote

from pycoin.services import spendables_for_address  # remote
from pycoin.key.validate import is_public_bip32_valid, is_address_valid
from pycoin.key.Key import Key
from pycoin.tx.tx_utils import create_signed_tx
from pycoin.tx.pay_to import ScriptMultisig, address_for_pay_to_script
from pycoin.encoding import EncodingError

from graphos.sources.model import ModelDataSource
from graphos.renderers import flot

from decimal import Decimal
from urllib2 import urlopen

#region Variables
master_public_key = Key.from_text('ITS_A_SECRET')
chikun_address = '12LmXkeVmSL3nBrMMBCPcLw2Jt97G1W4gr'
confirmations = 1
vig = Decimal('0.02')
v_key = 'ITS_A_SECRET'
#endregion

#########
# VIEWS #
#########
def home(request):
    #region GET
    if request.method == "GET":
        form_capcha = CaptchaTestForm()
        form_account = AccountForm()

        html_dtc = dict(form_capcha=form_capcha, form_account=form_account, count=len(AccountModel.objects.all()))

        error_message = request.session.get('error_message', False)
        if error_message:
            html_dtc.update(dict(error_message=error_message))
            del request.session['error_message']

        html_dtc.update(csrf(request))

        return render_to_response('chikun/home.html', html_dtc)
    #endregion
    #region POST
    if request.method == "POST":
# human test
        form = CaptchaTestForm(request.POST)
        if not form.is_valid():
            request.session.update(dict(error_message='Invalid Captcha'))
            return redirect('home')

# validate return address
        return_address = request.POST.get('return_address', False)
        if not is_address_valid(return_address):
            request.session.update(dict(error_message='Invalid Bitcoin Address'))
            return redirect('home')

# log details
        account_record = AccountModel.objects.create(return_address=return_address)
        account_record.save()

# deposit address
        deposit_address = master_public_key.subkey(account_record.id).address()

# html tags
        html_dtc = dict(deposit_address=deposit_address)
        html_dtc.update(csrf(request))

        return render_to_response('chikun/address.html', html_dtc)
    ''''''
    #endregion

def results(request):
    #region GET
    if request.method == 'GET':
        queryset = ResultModel.objects.all()

        if not queryset.exists():
            request.session.update(dict(error_message='No Results Available Yet'))
            return redirect('home')
    #endregion
    #region POST
    if request.method == 'POST':
        query = request.POST.get('search')

        queryset = ResultModel.objects.filter(winning_address=query) | ResultModel.objects.filter(winning_deposit=query)\
                  | ResultModel.objects.filter(losing_address=query) | ResultModel.objects.filter(losing_deposit=query)\
                  | ResultModel.objects.filter(txid=query)
    #endregion
    #region RETURN
    if queryset.exists():
        queryset = queryset.order_by('-id')
        data_source = ModelDataSource(queryset[:100], fields=['id', 'winning_deposit', 'losing_deposit'])
        chart = flot.LineChart(data_source)

        form = ResultsSearchForm()
        table = ResultsTable(queryset)
        RequestConfig(request, paginate=dict(per_page=100)).configure(table)

        html_dtc = dict(table=table, form=form, chart=chart)

        error_message = request.session.get('error_message', False)
        if error_message:
            html_dtc.update(dict(error_message=error_message))
            del request.session['error_message']

        html_dtc.update(csrf(request))

        return render(request, 'chikun/results.html', html_dtc)

    request.session.update(dict(error_message='No Result Found'))
    return redirect('results')
    #endregion

@csrf_exempt
def process(request):
    if request.method == 'POST':
        if request.POST.get('v_key') == v_key:
# check balance stats for all balance 0's
            zero_list = AccountModel.objects.filter(balance=0)
            if zero_list.exists():

                for i in zero_list:
                    address = master_public_key.subkey(i.id).address()
                    balance = Decimal(urlopen('https://blockchain.info/q/addressbalance/%s?confirmations=%s' % (address, confirmations)).read()) / 100000000

                    if balance >= Decimal('0.001'):
                        i.balance = balance

                    i.checked += 1
                    i.save()

# match valid accounts and make payments
            nonzero_list = AccountModel.objects.filter(balance__gt=0).order_by('?')
            if len(nonzero_list) > 1:
                v = True
                limit = len(nonzero_list) / 2 if not len(nonzero_list) % 2 else (len(nonzero_list) - 1) / 2
                nonzero_list = nonzero_list[:limit * 2]

            else:
                v = False

            if v:
                slice_one = nonzero_list[:limit]
                slice_two = nonzero_list[limit:]

                c = 0
                while c < limit:

                    if not slice_one[c].balance == slice_two[c].balance:
                        (winner, loser) = (slice_one[c], slice_two[c]) if slice_one[c].balance > slice_two[c].balance else (slice_two[c], slice_one[c])

                        winner_key = Key.from_text(request.POST['private_key']).subkey(winner.id)
                        loser_key = Key.from_text(request.POST['private_key']).subkey(loser.id)

                        try:
                            spendables = spendables_for_address(winner_key.address()) + spendables_for_address(loser_key.address())
                            signed_tx = create_signed_tx(spendables,
                                                         [(chikun_address, int((loser.balance * vig) * 100000000)), winner.return_address],
                                                         wifs=[winner_key.wif(), loser_key.wif()], fee="standard")

                            pushtx(signed_tx.as_hex())

                            ResultModel.objects.create(winning_address=winner_key.address(), winning_deposit=str(winner.balance),
                                                   losing_address=loser_key.address(), losing_deposit=str(loser.balance),
                                                   txid=signed_tx.id()).save()

                            for i in (winner, loser):
                                ArchiveModel.objects.create(**AccountModel.objects.filter(id=i.id).values()[0]).save()
                                AccountModel.objects.filter(id=i.id).delete()

                        except Exception as e:
                            lf = open('logFile', 'a')
                            print(e, file=lf)
                            lf.close()

                            for i in (winner, loser):
                                BrokenModel.objects.create(**AccountModel.objects.filter(id=i.id).values()[0]).save()
                                AccountModel.objects.filter(id=i.id).delete()

                    c += 1

# remove invalid accounts
            invalid_accounts = AccountModel.objects.filter(checked__gt=24).filter(balance=0)  # four hours
            if invalid_accounts.exists():

                for i in invalid_accounts:
                    InvalidModel.objects.create(**AccountModel.objects.filter(id=i.id).values()[0]).save()
                    AccountModel.objects.filter(id=i.id).delete()

            return HttpResponse(status=204)
