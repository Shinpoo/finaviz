# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from django.views.generic.list import ListView
from app import views
from app.views import CompanyList

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('company_info/<str:ticker>', views.company_info, name='company_info'),
    path('search/', views.SearchPage, name='search_result'),
    path('screener/', CompanyList.as_view(), name='screener'),
    re_path(r'^ajax_calls/search/',views.autocompleteModel),

    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

]
