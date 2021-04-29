from django.core.management.base import BaseCommand, CommandError
from app.models import Company
from app.company_manager import *
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Delete the specified tickers'

    def add_arguments(self, parser):
        parser.add_argument('ticker', nargs='+', type=str)

    def handle(self, *args, **options):
        for ticker in options['ticker']:
            manager = CompanyManager(ticker)
            try:
                manager.get_company()
            except:
                raise CommandError('Company "%s" does not exist in db.' % ticker)
            manager.c.delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted ticker "%s"' % ticker))
