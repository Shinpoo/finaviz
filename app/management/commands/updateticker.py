from django.core.management.base import BaseCommand, CommandError
from app.models import Company
from app.company_manager import *
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Update the specified tickers'

    def add_arguments(self, parser):
        parser.add_argument('ticker', nargs='+', type=str)

    def handle(self, *args, **options):
        for ticker in options['ticker']:
            try:
                manager = CompanyManager(ticker)
                manager.get_company()
            except Company.DoesNotExist:
                raise CommandError('Company "%s" does not exist' % ticker)

            manager.load_company()
            if manager.c.last_update.date() < datetime.today().date():
                manager.update_company()
            else:
                print("Company info already up to date.")
                

            manager.get_timeserie()
            if manager.timeserie.exists():
                manager.update_timeserie()
            else:
                raise CommandError('Timeserie "%s" does not exist' % ticker)

            manager.get_financials()
            if manager.financials.exists():
                manager.update_financials()
            else:
                raise CommandError('Financials "%s" does not exist' % ticker)

            manager.update_streaks()

            self.stdout.write(self.style.SUCCESS(
                'Successfully updated ticker "%s"' % ticker))
