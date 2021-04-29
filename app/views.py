# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present ['BHP', 'RDS.A', 'RDS.B', 'UL', 'CI', 'BF.B', 'MKCV', 'ACI', 'RLI', 'JW.B', 'JW.A', 'UBP', 'SBR', 'PTMN', 'AMNF']
"""
from django.db.models import query
from django.db.models.query import QuerySet
from app.utils import humanize_intlist
import calendar
from app.models import Company, Timeserie
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
import yfinance as yf
import simplejson as json
from datetime import datetime, timedelta
import dateutil.relativedelta
from django.db.models import Sum, Q
from django.db.models.functions import TruncYear
import pandas as pd
from django.views.generic import ListView
from django.core.paginator import Paginator


import humanize
from pprint import pprint
from app.company_manager import *
from .filters import CompanyFilter


# @login_required(login_url="/login/")
def index(request):
    # context = {}
    # context['segment'] = 'index'
    # context['datapoints'] = [0, 20, 10, 30, 15, 40, 20, 60, 80]
    # html_template = loader.get_template('index.html')
    # return HttpResponse(html_template.render(context, request))
    return redirect('screener')


# @login_required(login_url="/login/")
# def pages(request):
#     context = {}
#     # All resource paths end in .html.
#     # Pick out the html file name from the url. And load that template.
#     try:
#         tickers = ['AAPL', 'JNJ']
#         load_template = request.path.split('/')[-1]
#         context['segment'] = load_template
#         if load_template == "tables.html":
#             # context['guest_posters'] = GuestPoster.objects.all()
#             pass

#         html_template = loader.get_template(load_template)
#         return HttpResponse(html_template.render(context, request))

#     except template.TemplateDoesNotExist:

#         html_template = loader.get_template('page-404.html')
#         return HttpResponse(html_template.render(context, request))

#     except:

#         html_template = loader.get_template('page-500.html')
#         return HttpResponse(html_template.render(context, request))

# @login_required(login_url='/login/')

class  CompanyList(ListView):
    # return render(request, "screener.html", {})
    myFilter = CompanyFilter()
    template_name = "screener.html"
    paginate_by = 300
    model = Company
    ordering = ['-market_capitalization']
    sort_type = "down"

    def get_queryset(self) -> QuerySet:
        order_by = self.request.GET.get("order_by")
        sort_type = self.request.GET.get("sort")
        if order_by is not None:
            if sort_type == "down":
                self.sort_type = "up"
                queryset = Company.objects.order_by(order_by).exclude(trailing_pe_ratio__isnull=True)
            elif sort_type == "up":
                self.sort_type == "down"
                queryset = Company.objects.order_by("-"+order_by).exclude(trailing_pe_ratio__isnull=True)
            else: 
                queryset = super().get_queryset()
        else: 
            queryset = Company.objects.all().order_by("-market_capitalization")
        return queryset
        # if self.request.GET.get("order_by"):
        #     
        #     sort = self.request.GET.get("sort_type")
        #     if sort == "down":
        #         self.sort_type =="up"
        #         queryset = Company.objects.order_by(field)
        #         return queryset
        #     elif sort =="up":
        #         self.sort_type =="down"
        #         queryset = Company.objects.order_by("-"+field)
        #         return queryset
            # selection = self.request.GET.get("browse")
            # if selection == "Cats":
            #     queryset = Cats.objects.all()
            # elif selection == "Dogs":
            #     queryset = Dogs.objects.all()
            # elif selection == "Worms":
            #     queryset = Worms.objects.all()
            # else:
            #     queryset = Cats.objects.all()
        

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['sort_type'] = self.sort_type
        return context


def company_info(request, ticker):
    # ticker = 0
    # df_tick = pd.read_csv("app/sstickers.csv")
    # tickers_list = df_tick["Ticker"].to_list()
    # i = 0
    # bugged_tickers = []
    # for ticker in tickers_list:
    #     print(ticker, i)
    #     try:
    #         manager = CompanyManager(ticker)
    #         manager.get_or_create_or_update_company_info()
    #         manager.create_or_update_timeseries()
    #         manager.create_or_update_yearly_financials()
    #         i=i+1
    #     except:
    #         print("BUGGED", ticker)
    #         bugged_tickers.append(ticker)

    # print(bugged_tickers)
    # print("ho")
    manager = CompanyManager(ticker)
    manager.get_company()
    manager.get_timeserie()
    manager.get_financials()
    # manager.get_or_create_or_update_company_info()
    # manager.create_or_update_timeseries()
    # manager.create_or_update_yearly_financials()
    dividend_yield_date, dividend_yield = manager.get_yearly_dividends()
    c = manager.c
    context = {}
    context["name"] = c.name
    context["symbol"] = c.symbol,
    context["sector"] = c.sector
    context["industry"] = c.industry
    context["currency"] = c.currency
    context["website_url"] = c.website_url
    context["logo_url"] = c.logo_url
    context["description"] = c.description
    context["market_capitalization"] = c.market_capitalization
    context["market_price"] = c.market_price
    context["previous_close"] = c.previous_close
    context["trailing_pe_ratio"] = c.trailing_pe_ratio
    context["peg_ratio"] = c.peg_ratio
    context["pb_ratio"] = c.pb_ratio
    context["fifty_two_week_low"] = c.fifty_two_week_low
    context["fifty_two_week_high"] = c.fifty_two_week_high
    context["fifty_two_week_change"] = c.fifty_two_week_change
    context["beta"] = c.beta
    context["payout_ratio"] = c.payout_ratio
    context["dividend_yield"] = c.dividend_yield
    context["dividend_rate"] = c.dividend_rate
    #context = company.info.copy()
    # ts_1mo = Timeserie.objects.filter(company=c).order_by('-timestamp')[:31][::-1]
    # ts_1y = Timeserie.objects.filter(company=c).order_by('-timestamp')[:31*6][::-1]
    # ts_5y = Timeserie.objects.filter(company=c).order_by('-timestamp')[:12*31*6][::-1]
    # ts_max = Timeserie.objects.filter(company=c).order_by('timestamp')
    ts_1mo = manager.timeserie.filter(timestamp__gte=datetime.now() - dateutil.relativedelta.relativedelta(months=1)).order_by('timestamp')
    ts_1y = manager.timeserie.filter(timestamp__gte=datetime.now() - dateutil.relativedelta.relativedelta(years=1)).order_by('timestamp')
    ts_5y = manager.timeserie.filter(timestamp__gte=datetime.now() - dateutil.relativedelta.relativedelta(years=5)).order_by('timestamp')
    ts_max = manager.timeserie.order_by('timestamp')
    timestamp_1mo = [t.timestamp.strftime("%d-%b") for t in ts_1mo]
    timestamp_1y = [t.timestamp.strftime("%b %Y") for t in ts_1y]
    timestamp_5y = [t.timestamp.strftime("%b %Y") for t in ts_5y]
    timestamp_max = [t.timestamp.year for t in ts_max]
    price_1mo = [t.close for t in ts_1mo]
    price_1y = [t.close for t in ts_1y]
    price_5y = [t.close for t in ts_5y]
    price_max = [t.close for t in ts_max]

    context["price_y_max"] = json.dumps(price_max[::10])
    context["price_x_max"] = json.dumps(timestamp_max[::10])
    context["price_y_5y"] = json.dumps(price_5y)
    context["price_x_5y"] = json.dumps(timestamp_5y)  # json.dumps(list(history_5y.index.year)[::15])
    context["price_y_1y"] = json.dumps(price_1y)
    context["price_x_1y"] = json.dumps(timestamp_1y)
    context["price_y_1mo"] = json.dumps(price_1mo)
    context["price_x_1mo"] = json.dumps(timestamp_1mo)
    context["dividendyield_y_10y"] = json.dumps(dividend_yield[-10:])
    context["dividendyield_x_10y"] = json.dumps(dividend_yield_date[-10:])
    context["dividendyield_y_max"] = json.dumps(dividend_yield)
    context["dividendyield_x_max"] = json.dumps(dividend_yield_date)
    yearly_financials = manager.financials.order_by('timestamp')
    yearly_financials_timestamp = [yfin.timestamp.strftime("%Y") for yfin in yearly_financials]
    net_income = [yfin.net_income for yfin in yearly_financials]
    total_revenue = [yfin.total_revenue for yfin in yearly_financials]
    total_dividends = [yfin.total_dividends for yfin in yearly_financials]
    ts_1y =  manager.timeserie.filter(timestamp__gte=datetime.now() - dateutil.relativedelta.relativedelta(years=1)).order_by('timestamp')
    ts_5y =  manager.timeserie.filter(timestamp__gte=datetime.now() - dateutil.relativedelta.relativedelta(years=5)).order_by('timestamp')
    ts_max = manager.timeserie.order_by('timestamp')
    context["differenceFromLastClose"] = context["market_price"] -  context["previous_close"]
    context["differenceRelative"] = 100 * (context["market_price"] - context["previous_close"]) / context["previous_close"]

    totalrevenue_unit, totalrevenue_humanized = humanize_intlist(total_revenue)
    netincome_unit, netincome_humanized = humanize_intlist(net_income)
    totaldividends_unit, totaldividends_humanized = humanize_intlist(total_dividends)
    context["totalrevenue_y"] = json.dumps(totalrevenue_humanized)
    context["totalrevenue_x"] = json.dumps(yearly_financials_timestamp)
    context["netincome_y"] = json.dumps(netincome_humanized)
    context["netincome_x"] = json.dumps(yearly_financials_timestamp)
    context["totaldividendspaid_y"] = json.dumps(totaldividends_humanized)
    context["totaldividendspaid_x"] = json.dumps(yearly_financials_timestamp)
    context["totalrevenue_unit"] = totalrevenue_unit
    context["netincome_unit"] = netincome_unit
    context["totaldividendspaid_unit"] = totaldividends_unit
    # dividend_growth_streak = 0
    # dividend_streak = 0
    # reversed_dividend_yield =dividend_yield[::-1]
    # # print(reversed_dividend_yield)
    # stop_count = False
    # for year, div in enumerate(reversed_dividend_yield):
    #     # print(stop_count)
    #     if year == 0:
    #         if div > 0:
    #             dividend_growth_streak += 1
    #             dividend_streak +=1
    #         else:
    #             break
    #     else:
    #         if 0 < div < reversed_dividend_yield[year-1]:
    #             dividend_streak +=1
    #             if not stop_count:
    #                 dividend_growth_streak += 1
    #             # print(dividend_growth_streak, div , reversed_dividend_yield[year-1])
    #         elif div >= reversed_dividend_yield[year-1]:
    #             dividend_streak+=1
    #             stop_count = True
    #         else:
    #             break


    context["dividend_streak"] = c.dividend_streak
    context["dividend_growth_streak"] = c.dividend_growth_streak
    # print((datetime.now() - dateutil.relativedelta.relativedelta(years=1)).date())
    date_1y = datetime.today() - dateutil.relativedelta.relativedelta(years=1)
    date_5y = datetime.today() - dateutil.relativedelta.relativedelta(years=5)
    date_10y = datetime.today() - dateutil.relativedelta.relativedelta(years=10)
    date_20y = datetime.today() - dateutil.relativedelta.relativedelta(years=20)
    if date_1y.weekday() == 5:
        date_1y -= timedelta(days=1)
    elif date_1y.weekday() == 6:
        date_1y -= timedelta(days=2)
    if date_5y.weekday() == 5:
        date_5y -= timedelta(days=1)
    elif date_5y.weekday() == 6:
        date_5y -= timedelta(days=2)
    if date_10y.weekday() == 5:
        date_10y -= timedelta(days=2)
    elif date_10y.weekday() == 6:
        date_10y -= timedelta(days=3)
    if date_20y.weekday() == 5:
        date_20y -= timedelta(days=2)
    elif date_20y.weekday() == 6:
        date_20y -= timedelta(days=3)

    # stockprice_1y = Timeserie.objects.get(company=c, timestamp=date_1y).close
    # context["dividendpayout_growth_1y"] = (dividend_yield[-1] - dividend_yield[-2])/dividend_yield[-1]
    # context["dividendpayout_annualizedgrowth_1y"] = (1 + context["dividendpayout_growth_1y"])**(1/1) - 1
    # context["stockprice_growth_1y"] = (c.market_price - stockprice_1y)/stockprice_1y
    # context["stockprice_annualizedgrowth_1y"] = (1 + context["stockprice_growth_1y"])**(1/1) - 1

    # stockprice_5y = Timeserie.objects.get(company=c, timestamp=date_5y).close
    # context["dividendpayout_growth_5y"] = (dividend_yield[-1] - dividend_yield[-6])/dividend_yield[-1]
    # context["dividendpayout_annualizedgrowth_5y"] = (1 + context["dividendpayout_growth_5y"])**(1/5) - 1
    # context["stockprice_growth_5y"] = (c.market_price - stockprice_5y)/stockprice_5y
    # context["stockprice_annualizedgrowth_5y"] = (1 + context["stockprice_growth_5y"])**(1/5) - 1

    # stockprice_10y = Timeserie.objects.get(company=c, timestamp=date_10y).close
    # context["dividendpayout_growth_10y"] = (dividend_yield[-1] - dividend_yield[-11])/dividend_yield[-1]
    # context["dividendpayout_annualizedgrowth_10y"] = (1 + context["dividendpayout_growth_10y"])**(1/10) - 1
    # context["stockprice_growth_10y"] = (c.market_price - stockprice_10y)/stockprice_10y
    # context["stockprice_annualizedgrowth_10y"] = (1 + context["stockprice_growth_10y"])**(1/10) - 1
    try:
        stockprice_1y = manager.timeserie.get(timestamp=date_1y).close
        context["dividendpayout_growth_1y"] = (dividend_yield[-1] - dividend_yield[-2])/dividend_yield[-1]
        context["dividendpayout_annualizedgrowth_1y"] = (1 + context["dividendpayout_growth_1y"])**(1/1) - 1
        context["stockprice_growth_1y"] = (c.market_price - stockprice_1y)/stockprice_1y
        context["stockprice_annualizedgrowth_1y"] = (1 + context["stockprice_growth_1y"])**(1/1) - 1
    except:
        context["dividendpayout_growth_1y"] = None
        context["dividendpayout_annualizedgrowth_1y"] = None
        context["stockprice_growth_1y"] = None
        context["stockprice_annualizedgrowth_1y"] =None

    try:
        stockprice_5y = manager.timeserie.get(timestamp=date_5y).close
        context["dividendpayout_growth_5y"] = (dividend_yield[-1] - dividend_yield[-6])/dividend_yield[-1]
        context["dividendpayout_annualizedgrowth_5y"] = (1 + context["dividendpayout_growth_5y"])**(1/5) - 1
        context["stockprice_growth_5y"] = (c.market_price - stockprice_5y)/stockprice_5y
        context["stockprice_annualizedgrowth_5y"] = (1 + context["stockprice_growth_5y"])**(1/5) - 1
    except:
        context["dividendpayout_growth_5y"] = None
        context["dividendpayout_annualizedgrowth_5y"] = None
        context["stockprice_growth_5y"] = None
        context["stockprice_annualizedgrowth_5y"] =None

    try:
        stockprice_10y = manager.timeserie.get(timestamp=date_10y).close
        context["dividendpayout_growth_10y"] = (dividend_yield[-1] - dividend_yield[-11])/dividend_yield[-1]
        context["dividendpayout_annualizedgrowth_10y"] = (1 + context["dividendpayout_growth_10y"])**(1/10) - 1
        context["stockprice_growth_10y"] = (c.market_price - stockprice_10y)/stockprice_10y
        context["stockprice_annualizedgrowth_10y"] = (1 + context["stockprice_growth_10y"])**(1/10) - 1
    except:
        context["dividendpayout_growth_10y"] = None
        context["dividendpayout_annualizedgrowth_10y"] = None
        context["stockprice_growth_10y"] = None
        context["stockprice_annualizedgrowth_10y"] =None
    try:
        stockprice_20y = manager.timeserie.get(timestamp=date_20y).close
        context["dividendpayout_growth_20y"] = (dividend_yield[-1] - dividend_yield[-21])/dividend_yield[-1]
        context["dividendpayout_annualizedgrowth_20y"] = (1 + context["dividendpayout_growth_20y"])**(1/20) - 1
        context["stockprice_growth_20y"] = (c.market_price - stockprice_20y)/stockprice_20y
        context["stockprice_annualizedgrowth_20y"] = (1 + context["stockprice_growth_20y"])**(1/20) - 1
    except:
        context["dividendpayout_growth_20y"] = None
        context["dividendpayout_annualizedgrowth_20y"] = None
        context["stockprice_growth_20y"] = None
        context["stockprice_annualizedgrowth_20y"] =None
    
    context["last_update"] = c.last_update
    return render(request, "company_info.html", context)


def SearchPage(request):
    # products = product.objects.filter(name__icontains=srh)
    # params = {'products': products, 'search': srh}
    # render(request, 'company_info.html', context)
    return redirect('company_info', ticker=request.GET['query'].split(' ', 1)[0])

#df = pd.DataFrame(list(Timeserie.objects.filter(company=c).values()))
#df['timestamp'] = pd.to_datetime(df['timestamp'])
#df = df.set_index('timestamp').resample('1H').pad()
#df['Year'] = df.index.map(lambda x: x.year)


def autocompleteModel(request):
    if request.is_ajax():
        q = request.GET.get('term', '').capitalize()
        print(q, type(q))
        search_qs = Company.objects.filter(Q(symbol__startswith=q.upper()) | Q(name__startswith=q))
        results = []
        for r in search_qs:
            results.append(r.symbol +" "+r.name)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
