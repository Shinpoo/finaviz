# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Company(models.Model):
	# Text
	name = models.CharField(unique=True,max_length=100)
	symbol = models.CharField(unique=True, max_length=30)
	sector = models.CharField(max_length=30)
	industry = models.CharField(max_length=50)
	currency = models.CharField(blank=True,max_length=30)
	website_url = models.URLField()
	logo_url = models.URLField()
	description = models.TextField()
	isin = models.CharField(default="",max_length=30)
	

	# Numbers
	dividend_streak = models.IntegerField(null=True)
	dividend_growth_streak = models.IntegerField(null=True)
	market_capitalization = models.BigIntegerField(null=True)
	market_price = models.FloatField(null=True)
	previous_close = models.FloatField(null=True)
	trailing_pe_ratio = models.FloatField(null=True)
	peg_ratio = models.FloatField(null=True)
	pb_ratio = models.FloatField(null=True)
	fifty_two_week_low = models.FloatField(null=True)
	fifty_two_week_high = models.FloatField(null=True)
	fifty_two_week_change = models.FloatField(null=True)
	beta = models.FloatField(null=True)
	dividend_yield = models.FloatField(null=True)
	dividend_rate = models.FloatField(null=True)
	payout_ratio = models.FloatField(null=True)

	# #Date
	ex_dividend_date = models.DateField(null=True)
	last_dividend_date = models.DateField(null=True)
	last_update = models.DateTimeField(auto_now=True)


	def __str__(self):
		return self.name


class Timeserie(models.Model):
	# open = models.DecimalField(max_digits=8, decimal_places=2)
	# high = models.DecimalField(max_digits=8, decimal_places=2)
	# low = models.DecimalField(max_digits=8, decimal_places=2)
	# adjusted_close = models.DecimalField(max_digits=8, decimal_places=2)
	# volume = models.BigIntegerField()
	# adjusted_close = models.DecimalField(max_digits=8, decimal_places=2)
	# stock_splits = models.DecimalField(max_digits=6, decimal_places=2)
	timestamp = models.DateField()
	close = models.FloatField()
	dividends = models.FloatField()
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	
	class Meta:
		unique_together = ('timestamp', 'company')

class YearlyFinancials(models.Model):
	timestamp = models.DateField()
	total_dividends = models.BigIntegerField()
	total_revenue = models.BigIntegerField()
	net_income = models.BigIntegerField()
	company = models.ForeignKey(Company, on_delete=models.CASCADE)

	class Meta:
		unique_together = ('timestamp', 'company')

# from adaptor.model import CsvModel
# from adaptor.fields import CharField


# class myCsvModel(CsvModel):
#     blogName = CharField()
#     blogUrl = CharField()
#     niche = CharField()

#     class Meta:
#         delimiter = ","
