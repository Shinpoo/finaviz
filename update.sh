#!/usr/bin/env python

while read -r line; do
    python manage.py updateticker $line
done < tickers.txt