import calendar

from django.db.models.aggregates import Sum
from numpy.lib import financial
from app.models import Company, Timeserie, YearlyFinancials
import yfinance as yf
from datetime import datetime, timedelta
from itertools import groupby
from collections.abc import Iterable

class CompanyManager:
    def __init__(self, ticker):
        self.ticker = ticker
        self.yfcompany = None # ticker object from yfinance
        self.c = None
        self.timeserie = None
        self.financials = None

    def get_company(self):
        self.c = Company.objects.get(symbol=self.ticker)
    
    def get_timeserie(self):
        self.timeserie = Timeserie.objects.filter(company=self.c)

    def load_company(self): # Not accessible to website
        self.yfcompany = yf.Ticker(self.ticker)

    def get_financials(self):
        self.financials = YearlyFinancials.objects.filter(company=self.c)

    def update_company(self):
        self.c.isin = self.yfcompany.isin
        self.c.market_capitalization = self.yfcompany.info.get(
            "marketCap")
        self.c.market_price = self.yfcompany.info.get(
            "regularMarketPrice")  # change
        self.c.previous_close = self.yfcompany.info.get("previousClose")
        self.c.trailing_pe_ratio = self.yfcompany.info.get("trailingPE")
        self.c.peg_ratio = self.yfcompany.info.get("pegRatio")
        self.c.pb_ratio = self.yfcompany.info.get("priceToBook")
        self.c.fifty_two_week_low = self.yfcompany.info.get(
            "fiftyTwoWeekLow")
        self.c.fifty_two_week_high = self.yfcompany.info.get(
            "fiftyTwoWeekHigh")
        self.c.fifty_two_week_change = self.yfcompany.info.get(
            "52WeekChange")
        self.c.beta = self.yfcompany.info.get("beta")
        self.c.payout_ratio = self.yfcompany.info.get("payoutRatio")
        self.c.dividend_yield = self.yfcompany.info.get("dividendYield")
        self.c. dividend_rate = self.yfcompany.info.get("dividendRate")
        self.c.ex_dividend_date = None if (self.yfcompany.info.get(
            "exDividendDate") is None) else datetime.utcfromtimestamp(self.yfcompany.info.get("exDividendDate"))
        self.c.save()
        print(self.c, "Info updated")

    def update_timeserie(self):
        samples = []
        last_update = self.timeserie.latest('timestamp').timestamp #or last()
        time_delta = datetime.today().date() - last_update
        # weekday = datetime.today().weekday() Market is closed the weekend ! take this into account

        if time_delta.days <= 1:
            timeseries = yf.download(self.ticker, period="1d",interval="1d", actions=True, rounding=True)
        elif  4 > time_delta.days > 1: #security
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
        for t in timeseries.index: # Sometimes several row at the same date => check if iterable andd take only the first
            if self.timeserie.filter(timestamp=t).exists():
                print(self.c, t, "[Update] Timestamp already exists")
            else:
                if isinstance(timeseries.Dividends[t], Iterable):
                    samples.append(Timeserie(timestamp=t, close=timeseries.Close[t][0], dividends=float(timeseries.Dividends[t][0]), company=self.c))
                    print(self.c, t,"[Update] Timestamp added to sample")
                else:
                    samples.append(Timeserie(timestamp=t, close=timeseries.Close[t], dividends=float(timeseries.Dividends[t]), company=self.c))
                    print(self.c, t, "[Update] Timestamp added to sample")
        Timeserie.objects.bulk_create(samples)
        print(self.c, len(samples), "[Update] Timeserie samples added to DB")


    def update_financials(self):
        samples = []
        for t in self.yfcompany.financials.loc["Net Income"].index:
            if self.financials.filter(timestamp=t).exists():
                print(self.c, t, "[Update] Financial timestamp already exists")
            else:
                samples.append(YearlyFinancials(timestamp=t,
                total_dividends= int(-self.yfcompany.cashflow.loc["Dividends Paid"][t]),
                total_revenue=int(self.yfcompany.financials.loc["Total Revenue"][t]),
                net_income=int(self.yfcompany.financials.loc["Net Income"][t]),
                company=self.c))
                print(self.c, t, "[Update] Financial Timestamp added to sample")
        YearlyFinancials.objects.bulk_create(samples)
        print(self.c, len(samples),"[Update] Financials samples added to DB")

    def create_company(self):
        self.c = Company(name=self.yfcompany.info.get("longName"),
                         symbol=self.yfcompany.info.get("symbol"),
                         sector=self.yfcompany.info.get("sector") if self.yfcompany.info.get(
                             "sector") is not None else "",
                         industry=self.yfcompany.info.get("industry") if self.yfcompany.info.get(
                             "industry") is not None else "",
                         currency=self.yfcompany.info.get("currency") if self.yfcompany.info.get(
            "currency") is not None else "",
            website_url=self.yfcompany.info.get(
                "website") if self.yfcompany.info.get("website") is not None else "",
            logo_url=self.yfcompany.info.get("logo_url") if self.yfcompany.info.get(
            "logo_url") is not None else "",
            description=self.yfcompany.info.get("longBusinessSummary") if self.yfcompany.info.get(
            "longBusinessSummary") is not None else "",
            isin=self.yfcompany.isin,
            market_capitalization=self.yfcompany.info.get("marketCap"),
            market_price=self.yfcompany.info.get("regularMarketPrice"),
            previous_close=self.yfcompany.info.get("previousClose"),
            trailing_pe_ratio=self.yfcompany.info.get("trailingPE"),
            peg_ratio=self.yfcompany.info.get("pegRatio"),
            pb_ratio=self.yfcompany.info.get("priceToBook"),
            fifty_two_week_low=self.yfcompany.info.get("fiftyTwoWeekLow"),
            fifty_two_week_high=self.yfcompany.info.get("fiftyTwoWeekHigh"),
            fifty_two_week_change=self.yfcompany.info.get("52WeekChange"),
            beta=self.yfcompany.info.get("beta"),
            payout_ratio=self.yfcompany.info.get("payoutRatio"),
            dividend_yield=self.yfcompany.info.get("dividendYield"),
            dividend_rate=self.yfcompany.info.get("dividendRate"),
            ex_dividend_date=None if (self.yfcompany.info.get(
                "exDividendDate") is None) else datetime.utcfromtimestamp(self.yfcompany.info.get("exDividendDate"))
        )
        self.c.save()
        print(self.c, "Created.")

    def create_timeserie(self):
        timeseries = yf.download(self.ticker, period="max", interval="1d", actions=True, rounding=True)
        samples = []
        for t in timeseries.index:  # Sometimes several row at the same date => check if iterable andd take only the first
            if self.timeserie.filter(timestamp=t).exists():
                print(self.c, t, "[Create] Timestamp already exists. YOU SHOULD NEVER SEE THIS")
            else:
                if isinstance(timeseries.Dividends[t], Iterable):
                    samples.append(Timeserie(timestamp=t, close=timeseries.Close[t][0], dividends=float(timeseries.Dividends[t][0]), company=self.c))
                    print(self.c, t, "[Create] Timestamp added to sample")
                else:
                    samples.append(Timeserie(timestamp=t, close=timeseries.Close[t], dividends=float(timeseries.Dividends[t]), company=self.c))
                    print(self.c, t, "[Create] Timestamp added to sample")
        Timeserie.objects.bulk_create(samples)
        print(self.c, len(samples), "[Create] Timeserie samples added to DB")

    def create_financials(self):
        samples = []
        for t in self.yfcompany.financials.loc["Net Income"].index:
            if self.financials.filter(timestamp=t).exists():
                print(self.c, t, "[Create] Financial timestamp already exists. YOU  SHOULD NEVER SEE THIS")
            else:
                samples.append(YearlyFinancials(timestamp=t,
                total_dividends= int(-self.yfcompany.cashflow.loc["Dividends Paid"][t]),
                total_revenue=int(self.yfcompany.financials.loc["Total Revenue"][t]),
                net_income=int(self.yfcompany.financials.loc["Net Income"][t]),
                company=self.c))
                print(self.c, t, "[Create] Financial Timestamp added to sample")
        YearlyFinancials.objects.bulk_create(samples)
        print(self.c, len(samples),"[Create] Financials samples added to DB")
        
    # def get_or_create_or_update_company_info(self):
    #     # Company info
    #     try:
    #         self.c = Company.objects.get(symbol=self.ticker)
    #         if self.c.last_update.date() < datetime.today().date(): #DONT FORGET TO CHANGE <= to <
    #             #Update it
    #             self.yfcompany = yf.Ticker(self.ticker)
    #             self.c.isin = self.yfcompany.isin
    #             self.c.market_capitalization = self.yfcompany.info.get("marketCap")
    #             self.c.market_price = self.yfcompany.info.get("regularMarketPrice")  # change
    #             self.c.previous_close = self.yfcompany.info.get("previousClose")
    #             self.c.trailing_pe_ratio = self.yfcompany.info.get("trailingPE")
    #             self.c.peg_ratio = self.yfcompany.info.get("pegRatio")
    #             self.c.pb_ratio = self.yfcompany.info.get("priceToBook")
    #             self.c.fifty_two_week_low = self.yfcompany.info.get("fiftyTwoWeekLow")
    #             self.c.fifty_two_week_high = self.yfcompany.info.get("fiftyTwoWeekHigh")
    #             self.c.fifty_two_week_change = self.yfcompany.info.get("52WeekChange")
    #             self.c.beta = self.yfcompany.info.get("beta")
    #             self.c.payout_ratio = self.yfcompany.info.get("payoutRatio")
    #             self.c.dividend_yield = self.yfcompany.info.get("dividendYield")
    #             self.c. dividend_rate = self.yfcompany.info.get("dividendRate")
    #             self.c.ex_dividend_date = None if (self.yfcompany.info.get(
    #                 "exDividendDate") is None) else datetime.utcfromtimestamp(self.yfcompany.info.get("exDividendDate"))
    #             self.c.save()
    #         else:
    #             # get it
    #             pass
    #     except Company.DoesNotExist:
    #         # Create  it
    #         self.yfcompany = yf.Ticker(self.ticker)
    #         self.c = Company(name=self.yfcompany.info.get("longName"),
    #                     symbol=self.yfcompany.info.get("symbol"),
    #                     sector=self.yfcompany.info.get("sector") if self.yfcompany.info.get("sector") is not None else "",
    #                     industry=self.yfcompany.info.get("industry") if self.yfcompany.info.get("industry") is not None else "",
    #                     currency=self.yfcompany.info.get("currency") if self.yfcompany.info.get(
    #                         "currency") is not None else "",
    #                     website_url=self.yfcompany.info.get("website") if self.yfcompany.info.get("website") is not None else "",
    #                     logo_url=self.yfcompany.info.get("logo_url") if self.yfcompany.info.get(
    #                         "logo_url") is not None else "",
    #                     description=self.yfcompany.info.get("longBusinessSummary") if self.yfcompany.info.get(
    #                         "longBusinessSummary") is not None else "",
    #                     isin=self.yfcompany.isin,
    #                     market_capitalization=self.yfcompany.info.get("marketCap"),
    #                     market_price=self.yfcompany.info.get("regularMarketPrice"),
    #                     previous_close=self.yfcompany.info.get("previousClose"),
    #                     trailing_pe_ratio=self.yfcompany.info.get("trailingPE"),
    #                     peg_ratio=self.yfcompany.info.get("pegRatio"),
    #                     pb_ratio=self.yfcompany.info.get("priceToBook"),
    #                     fifty_two_week_low=self.yfcompany.info.get("fiftyTwoWeekLow"),
    #                     fifty_two_week_high=self.yfcompany.info.get("fiftyTwoWeekHigh"),
    #                     fifty_two_week_change=self.yfcompany.info.get("52WeekChange"),
    #                     beta=self.yfcompany.info.get("beta"),
    #                     payout_ratio=self.yfcompany.info.get("payoutRatio"),
    #                     dividend_yield=self.yfcompany.info.get("dividendYield"),
    #                     dividend_rate=self.yfcompany.info.get("dividendRate"),
    #                     ex_dividend_date=None if (self.yfcompany.info.get(
    #                         "exDividendDate") is None) else datetime.utcfromtimestamp(self.yfcompany.info.get("exDividendDate"))
    #                     )
    #         self.c.save()
    #     return self.c

        # Timeseries        
    # def create_or_update_timeseries(self):
    #     samples = []
    #     change_flag = True
    #     if Timeserie.objects.filter(company=self.c).exists():
    #         last_update = Timeserie.objects.filter(company=self.c).latest('timestamp').timestamp #or last()
    #         time_delta = datetime.today().date() - last_update
    #         # weekday = datetime.today().weekday() Market is closed the weekend ! take this into account
    #         if time_delta.days < 2:
    #             change_flag = False
    #         elif time_delta.days >= 2:
    #             timeseries = yf.download(self.ticker, period="1d",interval="1d", actions=True, rounding=True)
    #         elif  4 > time_delta.days > 1.5: #security
    #             timeseries = yf.download(self.ticker, period="5d", interval="1d", actions=True, rounding=True)
    #         elif 27 > time_delta.days >= 4:
    #             timeseries = yf.download(self.ticker, period="1mo", interval="1d", actions=True, rounding=True)
    #         elif 3*27 > time_delta.days >= 27: #use time_delta.months prolly
    #             timeseries = yf.download(self.ticker, period="3mo", interval="1d", actions=True, rounding=True)
    #         elif 6*27 > time_delta.days >= 3*27: #use time_delta.months prolly
    #             timeseries = yf.download(self.ticker, period="6mo", interval="1d", actions=True, rounding=True)
    #         elif 12*27 > time_delta.days >= 6*27:  # use time_delta.months prolly
    #             timeseries = yf.download(self.ticker, period="1y", interval="1d", actions=True, rounding=True)
    #         elif 2*12*27 > time_delta.days >= 12*27:  # use time_delta.months prolly
    #             timeseries = yf.download(self.ticker, period="2y", interval="1d", actions=True, rounding=True)
    #         elif 5*12*27 > time_delta.days >= 2*12*27:  # use time_delta.months prolly
    #             timeseries = yf.download(self.ticker, period="5y", interval="1d", actions=True, rounding=True)
    #         elif 10*12*27 > time_delta.days >= 5*12*27:  # use time_delta.months prolly
    #             timeseries = yf.download(self.ticker, period="5y", interval="1d", actions=True, rounding=True)
    #         else:
    #             timeseries = yf.download(self.ticker, period="max", interval="1d", actions=True, rounding=True)
    #     else:
    #         #create
    #         timeseries = yf.download(self.ticker, period="max", interval="1d", actions=True, rounding=True)
       
    #     if change_flag:
    #         for t in timeseries.index: # Sometimes several row at the same date => check if iterable andd take only the first
    #             print(self.c, t)
    #             if Timeserie.objects.filter(company=self.c, timestamp=t).exists():
    #                 pass
    #             else:
    #                 if isinstance(timeseries.Dividends[t], Iterable):
    #                     samples.append(Timeserie(timestamp=t, close=timeseries.Close[t][0], dividends=float(timeseries.Dividends[t][0]), company=self.c))
    #                 else:
    #                     samples.append(Timeserie(timestamp=t, close=timeseries.Close[t], dividends=float(timeseries.Dividends[t]), company=self.c))
    #         Timeserie.objects.bulk_create(samples)
    #     self.update_streaks()

        
    # def create_or_update_yearly_financials(self):
    #     samples = []
    #     change_flag = True
    #     if YearlyFinancials.objects.filter(company=self.c).exists():
    #         last_update = YearlyFinancials.objects.filter(company=self.c).latest('timestamp').timestamp  # or last()
    #         time_delta = datetime.now().date() - last_update
    #         if time_delta.days >= 365:
    #             #update
    #             if self.yfcompany is None:
    #                 self.yfcompany = yf.Ticker(self.ticker)
    #         else:
    #             #do nothing
    #             change_flag = False
    #     else:
    #         #create
    #         if self.yfcompany is None:
    #             self.yfcompany = yf.Ticker(self.ticker)
    #     if change_flag:
    #         for t in self.yfcompany.financials.loc["Net Income"].index:
    #             if YearlyFinancials.objects.filter(company=self.c, timestamp=t).exists():
    #                 pass
    #             else:
    #                 samples.append(YearlyFinancials(timestamp=t,
    #                 total_dividends= int(-self.yfcompany.cashflow.loc["Dividends Paid"][t]),
    #                 total_revenue=int(self.yfcompany.financials.loc["Total Revenue"][t]),
    #                 net_income=int(self.yfcompany.financials.loc["Net Income"][t]),
    #                 company=self.c))
    #         YearlyFinancials.objects.bulk_create(samples)


            
        
    def get_yearly_dividends(self):
        tseries =   self.timeserie.only('timestamp', 'dividends').order_by('timestamp')
        year_totals = {k: sum(x.dividends for x in g) for k, g in groupby(tseries, key=lambda i: i.timestamp.year)}
        years = list(year_totals.keys())[:-1]
        dividends = list(year_totals.values())[:-1]
        # print(year_totals)
        return years, dividends

    def update_streaks(self):
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
                elif div >= reversed_dividend_yield[year-1]:
                    dividend_streak += 1
                    stop_count = True
                else:
                    break
        self.c.dividend_streak = dividend_streak
        self.c.dividend_growth_streak = dividend_growth_streak
        self.c.save()
        print(self.c, "Streaks updated")
