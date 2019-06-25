# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 08:03:36 2019

@author: Christine
"""


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import matplotlib.dates as mdates
import datetime
plt.rcParams.update({'font.size': 14})
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import requests
import csv
import math
import urllib.request
import time
import numpy as np
import pickle
from bs4 import BeautifulSoup
import os

import time 
import datetime   
from sqlalchemy import create_engine 



class forum_scraper:
    def __init__(self):

        self.colnames_post = ['PostTitle','PostBody','UserName','FirstPostDate','ResponseCount','SubForumName']
        self.colnames_user = ['Username','JoinDate','LastActiveDate','NumPosts','Num14ers','Num13ers','MaxSkill','ClimbPreference','Accomplishments','Goals','GearList','Interests','Location','CountTripReports']
        self.colnames_cond_report = ['PeakName','DateClimb','DatePost','Route','Username','ReportText']
        self.peak_cond_url = r'https://www.14ers.com/php14ers/peakstatus_main.php'
        self.forum_base_url = r'https://www.14ers.com/forum/viewforum.php?f='

    def build_conditions_dataframe(self):
        peakinfo = self.get_conditions_links()
        self.peakinfo = peakinfo
        peakcond_df = self.get_reports_from_links(peakinfo)
        return peakcond_df

    def get_conditions_links(self):
        
        ## Returns a list of tuples to: (first page of the condition report for each peak, peak range,peak name) 
        peak_cond_base = r'https://www.14ers.com/php14ers'
        response = requests.get(self.peak_cond_url)
        soup = BeautifulSoup(response.text,'html')
        range_tables = soup.findAll("table", {"class": "data_box2 CopyR1 smallfontadjust"})
        for n in range(len(range_tables)):
            rows = range_tables[n].findAll("tr")
            range_name = (rows[0].findAll("div",{"class":"show-12"}))[0].text
            ptable = rows[1].findAll("table", {"class": "peakTable"})
            alin=ptable[0].findAll("a",href=True)  ##loop through list of peaks
            for m in range(len(alin)):
                link = alin[m]['href']
                if n==0 and m==0:
                    peakinfo = [(peak_cond_base + link[1::],range_name,alin[0].text.strip())]
                else:
                    peakinfo.append((peak_cond_base + link[1::],range_name,alin[m].text.strip()))
            
        return peakinfo
    
    def get_reports_from_links(self,peakinfo):
        entryList = []
        for n in range(len(peakinfo)):  ##each of the mountains
            url = peakinfo[n][0]
            range_name = peakinfo[n][1]
            mtn_name = peakinfo[n][2]
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html')
            pagenums = soup.findAll("div",{"class":"pagination"})
            pagenums=pagenums[0].text.split('...')
            print(mtn_name)
            print(pagenums)
            if len(pagenums)>1:
                lastnum = int(pagenums[-1].strip()[:-1])
            else:
                try:
                    lastnum = int(pagenums[0][-3])
                except:
                    lastnum=1
            for m in range((lastnum)):  ## each of the subpages
                pageurl = url + r'&start=' + str(m*20)
                response = requests.get(pageurl)
                soup = BeautifulSoup(response.text, 'html') 
               # dateClimb = soup.findAll("div",{"class":"buttonf orangef"})
                peakTable = soup.findAll("table",{"class":"data_box2 breaklines rowhover"})[0]
                peakRows = peakTable.findAll("tr")[1::]
                for p in range(len(peakRows)):
                    dateEntry = peakRows[p].findAll("div",{"class":"buttonf orangef"})[0].text
                    dateEntry = pd.to_datetime(dateEntry).strftime('%Y-%m-%d %H:%M:%S')
                    entryTextTable = ((peakRows[p]).findAll("div")[1].text).split('\xa0')
                    routeClimb = entryTextTable[1][0:-10]
                    user = entryTextTable[3][0:-5]
                    entryText = entryTextTable[4]
                    entryDict = {'PeakName':mtn_name,'PeakRange':range_name,'DateEntry':dateEntry,'User':user,'RouteClimb':routeClimb,'EntryText':entryText}
                    entryList.append(entryDict)
        df = pd.DataFrame(data = entryList)
        return df    



if __name__ == "__main__":
    fs = forum_scraper() 
    cond_df = fs.build_conditions_dataframe()
    fname = r'conditions_df.pkl'
    with open(fname, 'wb') as handle:
        pickle.dump(cond_df, handle)
    
