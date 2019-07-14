# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:01:39 2019

@author: Christine
"""

from flask import Flask, jsonify, request
import pickle
import pandas as pd
app = Flask(__name__)


@app.route(r'/rec14er/', methods=['GET','POST'])
def predict14er():
    print("hello guys")
    try:
        uname = request.get_json()['Username']
        urows = users[users['Username']==uname]
        if len(urows) == 0:
            print ('Requested User Does Not Exist in Database')
            return ('Requested User Does Not Exist in Database')
        else:
            uid = (urows.iloc[0])['NewUserId']
            common_peaks = ['GraysPeak', 'MtBierstadt', 'QuandaryPeak', 'TorreysPeak', 'MtDemocrat', 'MtElbert', 'MtBross', 'MtCameron', 'MtEvans', 'MtSherman', 'PikesPeak']
            user_prediction=pred.astype('float')
            args=((-user_prediction[uid,:]).argsort())
            hiked_list = (users[users['NewUserId']==uid])['PeakName'].tolist()
            print('User' + str(uname) + 'Hiked:')
            print(hiked_list)
            index_ind=users[['PeakId','PeakName']]
            rec_list = index_ind['PeakName'][args].tolist()
            new_rec_list = [elem for elem in rec_list if elem not in hiked_list and elem not in common_peaks]
            print('\n\n')
            print('Recommendation for User' + str(uname) + ':')
            print(new_rec_list[0:12])
            return jsonify({'HikedList':hiked_list,'RecList':new_rec_list[0:12]})
    except:
        return "Error reading your input"
    
@app.route("/")
@app.route("/home")
def hello():
    return r'Hi all!  Note that users with winter climbs logged are currently being added to the database; sit tight!'  #@app.route("/Flask/")

if __name__ == '__main__':
   # app.run(debug=True)
    
    recfile = r'models/user_prediction_full'
    userfile = r'models/14ers_df_final'
    pred = pickle.load(open(recfile, 'rb'))
    users = pickle.load(open(userfile,'rb'))
   # uprof = pickle.load(open(r'user_profile_data_FULL',"rb"))
    app.run(debug=True)