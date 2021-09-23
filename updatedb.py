import os

my_list = open("tickers.txt").read().splitlines()

os.system("python manage.py updateticker "+" ".join(my_list))
