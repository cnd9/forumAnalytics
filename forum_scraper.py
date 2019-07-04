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
from forum_scrape_utils import number_from_string
import time 
import datetime   
from sqlalchemy import create_engine 



class forum_scraper:
    def __init__(self):

        self.colnames_post = ['PostTitle','PostBody','UserName','FirstPostDate','ResponseCount','SubForumName']
        self.colnames_user = ['UserId','Username','Age','MaxSkillLevel','ClimbingPreference','Accomplishments','Goals','MyGearList','Location','Occupation','Num14ers','Num13ers','NumPhotos','NumTripReports','NumClimbTimes','GearForSale','JoinDate','LastActiveDate','NumPosts']
        self.colnames_cond_report = ['PeakName','DateClimb','DatePost','Route','Username','ReportText']
        self.peak_cond_url = r'https://www.14ers.com/php14ers/peakstatus_main.php'
        self.forum_base_url = r'https://www.14ers.com/forum/viewforum.php?f='
        self.n_users = 86101
        
    def build_conditions_dataframe(self):
        peakinfo = self.get_conditions_links()
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
                self.resp = soup
 
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
        self.dftest = entryList
        return df    
    
    def build_user_profile_dataframe(self):
        form_data = {'username': 'forum_researcher','password': 'ForumResearcher1','redirect': './ucp.php?mode=login','sid': 'e1ba96ab85c15a9b2a7a5a1b7be552e8','redirect': 'index.php','login': 'Login'}
        login_post_url = r'https://www.14ers.com/forum/ucp.php?mode=login'
        user_df = pd.DataFrame(columns = self.colnames_user)

        with requests.Session() as sesh:
            sesh.post(login_post_url, data=form_data)
            for n in range(3,self.n_users):
                print(n)
                response = sesh.get(r'https://www.14ers.com/forum/memberlist.php?mode=viewprofile&u='+str(n))
                soup = BeautifulSoup(response.text, 'html')
                self.souptest = soup 
                ## below get the fields for the user dataframe besides joindate, lastactivedate, and number of posts
                profile_info = soup.findAll("dl",{'class':'left-box details profile-details'})
                if len(profile_info) > 0:
                    profile_fields = profile_info[0].findAll('dt')
                    profile_fields = [(elem.text.strip(':')).replace(" ", "") for elem in profile_fields]
                    profile_data = profile_info[0].findAll('dd')
                    profile_data = [elem.text.strip() for elem in profile_data]
                    user_field_dict = {elem:'' for elem in self.colnames_user}
                    for m in range(len(profile_fields)):
                        if profile_fields[m] in self.colnames_user:
                            user_field_dict[profile_fields[m]] = profile_data[m]
                    try:
                        user_field_dict['Num14ers'] = int(profile_data[profile_fields.index('14erChecklist')])
                    except:
                        user_field_dict['Num14ers'] = np.nan
                    try:
                        user_field_dict['Num13ers'] = int(profile_data[profile_fields.index('13erChecklist')])
                    except:
                        user_field_dict['Num13ers'] = np.nan 
                    user_field_dict['NumPhotos'] = number_from_string(profile_data[profile_fields.index('MyPhotos')])
                    user_field_dict['NumTripReports'] = number_from_string(profile_data[profile_fields.index('MyTripReports')])
                    user_field_dict['NumClimbTimes'] = number_from_string(profile_data[profile_fields.index('MyClimbTimes')])
                    user_field_dict['GearForSale'] = (profile_data[profile_fields.index('MyClassifieds')]).strip()
                    user_field_dict['UserId'] = n
                    
                    ##below get the remaining fields for the user dataframe
                    stats_info = soup.findAll("div",{'class':'column2'})
                    stats_info = stats_info[0].findAll('dl')
                    stats_fields = stats_info[0].findAll('dt')
                    stats_fields = [(elem.text.strip(':')).replace(" ", "") for elem in stats_fields]
                    stats_data = stats_info[0].findAll('dd')
                    stats_data = [elem.text.strip() for elem in stats_data]
                    self.sdtest = stats_data[0]
                    user_field_dict['JoinDate'] = pd.to_datetime(stats_data[0])
                    try:
                        user_field_dict['LastActiveDate'] = pd.to_datetime(stats_data[1])
                    except:
                        user_field_dict['LastActiveDate'] = pd.NaT
                    user_field_dict['NumPosts'] = int(stats_data[2].split(' ')[0])
                    user_df = user_df.append(user_field_dict,ignore_index=True)
                    
            return user_df
                
    def build_peakchecklist_dataframe(self):
        fname_user_full = r'user_profile_data_FULL'
        user_df = pickle.load(open(fname_user_full,"rb"))
        users_14erList = user_df[user_df['Num14ers'] > 0]
        users_13erList = user_df[user_df['Num13ers']>0]
        dfcols = ['UserId','PeakName','NumClimbs']
        df_13erList = pd.DataFrame(columns=dfcols)
        df_14erList = pd.DataFrame(columns=dfcols)
        with requests.Session() as sesh:
            sesh.post(self.login_post_url, data=self.form_data)
            for n in range(len(users_13erList)):
                uid = users_13erList['UserId'].iloc[n]
                print(users_13erList['Username'].iloc[n])
                url_13er_list = r'https://www.14ers.com/php14ers/usrpeaksv.php?usernum='+str(uid)+r'&checklist=13ers&rk=both&nm=both&peakstoshow=climbed&listd=range&showicons=on'
                response = requests.get(url_13er_list)
                soup = BeautifulSoup(response.text, 'html')
                range_tables = soup.findAll('table',{'class':'data_box2 rowhover'})
                for m in range(len(range_tables)):
                    trs = range_tables[m].findAll('tr')
                    if len(trs)>1:
                        for q in range(1,len(trs)-1):
                            peakinfo = trs[q].text.strip()
                            n_climbs = number_from_string(peakinfo)
                            peak_name = alpha_from_string(peakinfo)
                            entry = {'UserId':int(uid),'PeakName':peak_name,'NumClimbs':n_climbs}
                            df_13erList=df_13erList.append(entry,ignore_index=True)
            self.df13ers = df_13erList
            fname_13er = r'13erChecklistByUser_df'
            with open(fname_13er, 'wb') as handle:
                pickle.dump(df_13erList, handle)    
            
            #Now repeat for the 14er Checklists
            for n in range(len(users_14erList)):
                uid = users_14erList['UserId'].iloc[n]
                print(users_14erList['Username'].iloc[n])
                url_14er_list = r'https://www.14ers.com/php14ers/usrpeaksv.php?usernum='+str(uid)+r'&checklist=14ers&rk=both&nm=both&peakstoshow=climbed&listd=range&showicons=on'

                response = requests.get(url_14er_list)
                soup = BeautifulSoup(response.text, 'html')
                range_tables = soup.findAll('table',{'class':'data_box2 rowhover'})
                for m in range(len(range_tables)):
                    trs = range_tables[m].findAll('tr')
                    if len(trs)>1:
                        for q in range(1,len(trs)-1):
                            peakinfo = trs[q].text.strip()
                            n_climbs = number_from_string(peakinfo)
                            peak_name = alpha_from_string(peakinfo)
                            entry = {'UserId':int(uid),'PeakName':peak_name,'NumClimbs':n_climbs}
                            df_14erList=df_14erList.append(entry,ignore_index=True)
            fname_14er = r'14erChecklistByUser_df'
            with open(fname_14er, 'wb') as handle:
                pickle.dump(df_14erList, handle)                   



if __name__ == "__main__":
    fs = forum_scraper() 
   # cond_df = fs.build_conditions_dataframe()
    user_df = fs.build_user_profile_dataframe()
    fname_cond = r'conditions_df.pkl'
    fname_user = r'user_profile_data.pkl'
  #  with open(fname, 'wb') as handle:
  #      pickle.dump(cond_df, handle)
    with open(fname_user, 'wb') as handle:
        pickle.dump(user_df, handle)
