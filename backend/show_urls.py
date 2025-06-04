#!/usr/bin/env python
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

from django.urls import get_resolver

def show_urls(urllist, depth=0):
    for entry in urllist:
        print("  " * depth + str(entry.pattern) + " -> " + str(entry.callback))
        if hasattr(entry, 'url_patterns'):
            show_urls(entry.url_patterns, depth + 1)

resolver = get_resolver()
show_urls(resolver.url_patterns)
