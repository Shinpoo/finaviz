import calendar

from django.db.models.aggregates import Sum
from app.models import Company, Timeserie, YearlyFinancials
import yfinance as yf
from datetime import datetime, timedelta
from itertools import groupby
from collections.abc import Iterable

class CompanyManager:
    def __init__(self, ticker):
        self.ticker = ticker
        self.company = None # ticker object from yfinance
        self.c = None

    def get_or_create_or_update_company_info(self):
        # Company info
        try:
            self.c = Company.objects.get(symbol=self.ticker)
            if self.c.last_update.date() < datetime.today().date(): #DONT FORGET TO CHANGE <= to <
                #Update it
                self.company = yf.Ticker(self.ticker)
                self.c.isin = self.company.isin
                self.c.market_capitalization = self.company.info.get("marketCap")
                self.c.market_price = self.company.info.get("regularMarketPrice")  # change
                self.c.previous_close = self.company.info.get("previousClose")
                self.c.trailing_pe_ratio = self.company.info.get("trailingPE")
                self.c.peg_ratio = self.company.info.get("pegRatio")
                self.c.pb_ratio = self.company.info.get("priceToBook")
                self.c.fifty_two_week_low = self.company.info.get("fiftyTwoWeekLow")
                self.c.fifty_two_week_high = self.company.info.get("fiftyTwoWeekHigh")
                self.c.fifty_two_week_change = self.company.info.get("52WeekChange")
                self.c.beta = self.company.info.get("beta")
                self.c.payout_ratio = self.company.info.get("payoutRatio")
                self.c.dividend_yield = self.company.info.get("dividendYield")
                self.c. dividend_rate = self.company.info.get("dividendRate")
                self.c.ex_dividend_date = None if (self.company.info.get(
                    "exDividendDate") is None) else datetime.utcfromtimestamp(self.company.info.get("exDividendDate"))
                self.c.save()
            else:
                # get it
                pass
        except Company.DoesNotExist:
            # Create  it
            self.company = yf.Ticker(self.ticker)
            self.c = Company(name=self.company.info.get("longName"),
                        symbol=self.company.info.get("symbol"),
                        sector=self.company.info.get("sector") if self.company.info.get("sector") is not None else "",
                        industry=self.company.info.get("industry") if self.company.info.get("industry") is not None else "",
                        currency=self.company.info.get("currency") if self.company.info.get(
                            "currency") is not None else "",
                        website_url=self.company.info.get("website") if self.company.info.get("website") is not None else "",
                        logo_url=self.company.info.get("logo_url") if self.company.info.get(
                            "logo_url") is not None else "",
                        description=self.company.info.get("longBusinessSummary") if self.company.info.get(
                            "longBusinessSummary") is not None else "",
                        isin=self.company.isin,
                        market_capitalization=self.company.info.get("marketCap"),
                        market_price=self.company.info.get("regularMarketPrice"),
                        previous_close=self.company.info.get("previousClose"),
                        trailing_pe_ratio=self.company.info.get("trailingPE"),
                        peg_ratio=self.company.info.get("pegRatio"),
                        pb_ratio=self.company.info.get("priceToBook"),
                        fifty_two_week_low=self.company.info.get("fiftyTwoWeekLow"),
                        fifty_two_week_high=self.company.info.get("fiftyTwoWeekHigh"),
                        fifty_two_week_change=self.company.info.get("52WeekChange"),
                        beta=self.company.info.get("beta"),
                        payout_ratio=self.company.info.get("payoutRatio"),
                        dividend_yield=self.company.info.get("dividendYield"),
                        dividend_rate=self.company.info.get("dividendRate"),
                        ex_dividend_date=None if (self.company.info.get(
                            "exDividendDate") is None) else datetime.utcfromtimestamp(self.company.info.get("exDividendDate"))
                        )
            self.c.save()
        return self.c

        # Timeseries
    def create_or_update_timeseries(self):
        samples = []
        change_flag = True
        if Timeserie.objects.filter(company=self.c).exists():
            last_update = Timeserie.objects.filter(company=self.c).latest('timestamp').timestamp #or last()
            time_delta = datetime.today().date() - last_update
            # weekday = datetime.today().weekday() Market is closed the weekend ! take this into account
            if time_delta.days < 2:
                change_flag = False
            elif time_delta.days >= 2:
                timeseries = yf.download(self.ticker, period="1d",interval="1d", actions=True, rounding=True)
            elif  4 > time_delta.days > 1.5: #security
                timeseries = yf.download(self.ticker, period="5d", interval="1d", actions=True, rounding=True)
            elif 27 > time_delta.days >= 4:
                timeseries = yf.download(self.ticker, period="1mo", interval="1d", actions=True, rounding=True)
            elif 3*27 > time_delta.days >= 27: #use time_delta.months prolly
                timeseries = yf.download(self.ticker, period="3mo", interval="1d", actions=True, rounding=True)
            elif 6*27 > time_delta.days >= 3*27: #use time_delta.months prolly
                timeseries = yf.download(self.ticker, period="6mo", interval="1d", actions=True, rounding=True)
            elif 12*27 > time_delta.days >= 6*27:  # use time_delta.months prolly
                timeseries = yf.download(self.ticker, period="1y", interval="1d", actions=True, rounding=True)
            elif 2*12*27 > time_delta.days >= 12*27:  # use time_delta.months prolly
                timeseries = yf.download(self.ticker, period="2y", interval="1d", actions=True, rounding=True)
            elif 5*12*27 > time_delta.days >= 2*12*27:  # use time_delta.months prolly
                timeseries = yf.download(self.ticker, period="5y", interval="1d", actions=True, rounding=True)
            elif 10*12*27 > time_delta.days >= 5*12*27:  # use time_delta.months prolly
                timeseries = yf.download(self.ticker, period="5y", interval="1d", actions=True, rounding=True)
            else:
                timeseries = yf.download(self.ticker, period="max", interval="1d", actions=True, rounding=True)
        else:
            #create
            timeseries = yf.download(self.ticker, period="max", interval="1d", actions=True, rounding=True)
       
        if change_flag:
            for t in timeseries.index: # Sometimes several row at the same date => check if iterable andd take only the first
                if Timeserie.objects.filter(company=self.c, timestamp=t).exists():
                    pass
                else:
                    if isinstance(timeseries.Dividends[t], Iterable):
                        samples.append(Timeserie(timestamp=t, close=timeseries.Close[t], dividends=float(timeseries.Dividends[t][0]), company=self.c))
                    else:
                        samples.append(Timeserie(timestamp=t, close=timeseries.Close[t], dividends=float(timeseries.Dividends[t]), company=self.c))
            Timeserie.objects.bulk_create(samples)
        self.get_streaks()

        
    def create_or_update_yearly_financials(self):
        samples = []
        change_flag = True
        if YearlyFinancials.objects.filter(company=self.c).exists():
            last_update = Timeserie.objects.filter(company=self.c).latest('timestamp').timestamp  # or last()
            time_delta = datetime.now().date() - last_update
            if time_delta.days >= 365:
                #update
                if self.company is None:
                    self.company = yf.Ticker(self.ticker)
            else:
                #do nothing
                change_flag = False
        else:
            #create
            if self.company is None:
                self.company = yf.Ticker(self.ticker)
        if change_flag:
            for t in self.company.financials.loc["Net Income"].index:
                if YearlyFinancials.objects.filter(company=self.c, timestamp=t).exists():
                    pass
                else:
                    samples.append(YearlyFinancials(timestamp=t,
                    total_dividends= int(-self.company.cashflow.loc["Dividends Paid"][t]),
                    total_revenue=int(self.company.financials.loc["Total Revenue"][t]),
                    net_income=int(self.company.financials.loc["Net Income"][t]),
                    company=self.c))
            YearlyFinancials.objects.bulk_create(samples)


            
        
    def get_yearly_dividends(self):
        tseries = Timeserie.objects.filter(company=self.c).only('timestamp', 'dividends').order_by('timestamp')
        year_totals = {k: sum(x.dividends for x in g) for k, g in groupby(tseries, key=lambda i: i.timestamp.year)}
        years = list(year_totals.keys())[:-1]
        dividends = list(year_totals.values())[:-1]
        # print(year_totals)
        return years, dividends

    def get_streaks(self):
        y, dividend_yield = self.get_yearly_dividends()
        dividend_growth_streak = 0
        dividend_streak = 0
        reversed_dividend_yield = dividend_yield[::-1]
        # print(reversed_dividend_yield)
        stop_count = False
        for year, div in enumerate(reversed_dividend_yield):
            # print(stop_count)
            if year == 0:
                if div > 0:
                    dividend_growth_streak += 1
                    dividend_streak += 1
                else:
                    break
            else:
                if 0 < div < reversed_dividend_yield[year-1]:
                    dividend_streak += 1
                    if not stop_count:
                        dividend_growth_streak += 1
                    # print(dividend_growth_streak, div , reversed_dividend_yield[year-1])
                elif div >= reversed_dividend_yield[year-1]:
                    dividend_streak += 1
                    stop_count = True
                else:
                    break
        self.c.dividend_streak = dividend_streak
        self.c.dividend_growth_streak = dividend_growth_streak
        self.c.save()
