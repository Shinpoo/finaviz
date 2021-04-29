from django.core.management.base import BaseCommand, CommandError
from app.models import Company
from app.company_manager import *
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Create the specified tickers'

    def add_arguments(self, parser):
        parser.add_argument('ticker', nargs='+', type=str)

    def handle(self, *args, **options):
        for ticker in options['ticker']:
            manager = CompanyManager(ticker)
            try:
                manager.load_company()
            except:
                raise CommandError('Company "%s" does not exist on yfinance' % ticker)
            try:
                manager.create_company()
            except:
                raise CommandError('Company "%s" cannot be created' % ticker)

            manager.get_timeserie()
            if manager.timeserie.exists():
                raise CommandError('Timeserie for "%s" already exists, cannot be created' % ticker)
            else:
                manager.create_timeserie()
            
            manager.get_financials()
            if manager.financials.exists():
                raise CommandError('Financials for "%s" already exists, cannot be created' % ticker)
            else:
                manager.create_financials()

            

            manager.update_streaks()
            self.stdout.write(self.style.SUCCESS(
                'Successfully added ticker "%s"' % ticker))
