import django_tables2 as tables
from models import ResultModel

class ResultsTable(tables.Table):
    # winning_address = tables.TemplateColumn('<a href="https://test-insight.bitpay.com/address/{{record.winning_address}}" target="_blank">{{record.winning_address}}</a>')
    # winning_deposit = tables.TemplateColumn('<a href="https://test-insight.bitpay.com/tx/{{record.winning_output_transaction_hash}}" target="_blank">{{record.winning_deposit}}</a>')
    # losing_deposit = tables.TemplateColumn('<a href="https://test-insight.bitpay.com/tx/{{record.losing_output_transaction_hash}}" target="_blank">{{record.losing_deposit}}</a>')
    # losing_address = tables.TemplateColumn('<a href="https://test-insight.bitpay.com/address/{{record.losing_address}}" target="_blank">{{record.losing_address}}</a>')
    txid = tables.TemplateColumn('<a href="https://blockchain.info/tx/{{record.txid}}" target="_blank">{{record.txid}}</a>')
    class Meta:
        model = ResultModel
        attrs = {"class": "paleblue"}
