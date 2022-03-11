import os
import re
from tqdm import tqdm
import sqlite3


xmlfile = 'enmemoryalpha_pages_current.xml'

def read1():
    return xml.read(29191061)

with open(xmlfile, 'r', encoding="utf=8") as xml:
    for fname in iter(read1, ''):
        labels = re.findall(r'<page>([\S\s]+?)<\/page>', fname)
        for item in labels:
            try:
                ns = re.search(r'<ns>([\S\s]+?)<\/ns>', item)
            except:
                ns = 'None'
            try:
                title = re.search(r'<title>([\S\s]+?)<\/title>', item)
            except:
                title = 'None'
            try:
                txt = re.search(r'<text xml.+([\S\s]+?)<\/text>', item)
            except:
                txt = 'None'
            if '0' in str(ns.group(1)):
                try:
                    stuff = title.group(1), ns.group(1), txt.group(1)
                except:
                    stuff = title.group(1), ns.group(1), 'None'
                print(stuff)
