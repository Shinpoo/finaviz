# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Company, Timeserie, YearlyFinancials


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('last_update','name', 'symbol', 'sector', 'market_price', 'payout_ratio','dividend_yield')
    list_filter = ['last_update', 'sector']


class TimeserieAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'close', 'dividends','get_company')

    def get_company(self, obj):
        return obj.company.name
    
    get_company.admin_order_field = 'company' # Column order sorting
    get_company.short_description = 'Company Name' #Rename column head

    list_filter = ['timestamp', 'company__name']


class YearlyFinancialsAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'net_income', 'total_revenue', 'total_dividends', 'get_company')

    def get_company(self, obj):
        return obj.company.name

    get_company.admin_order_field = 'company'  # Column order sorting
    get_company.short_description = 'Company Name'  # Rename column head

    list_filter = ['timestamp', 'company__name']

admin.site.register(Company, CompanyAdmin)
admin.site.register(Timeserie, TimeserieAdmin)
admin.site.register(YearlyFinancials, YearlyFinancialsAdmin)
