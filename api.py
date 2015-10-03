#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask, flask.views
from flask import Flask,flash, render_template, request, redirect, url_for, send_from_directory
app = Flask(__name__)
from parse_rest.connection import register
from parse_rest.datatypes import Object, GeoPoint
from parse_rest.user import User
from flask import jsonify
import operator
import time
import json
from random import randint
import os
from cron import manual_scrape,SERVER_URL,dir_path,Videos

from azure.storage.blob import BlobService
blob_service = BlobService(account_name='chestreamraw', account_key='ZzW37B0CbPC8ms99/IgN7Ae4VCx0z9gYtvncJ0GqorFnvbc6GAA6O0Vxrk2dlasiaTmrokxDS3iW5eQ0DEEAfw==')


parse_credentials = {
    "application_id": "M5tnZk2K6PdF82Ra8485bG2VQwPjpeZLeL96VLPj",
    "rest_api_key": "VBGkzL4uHsOw0K1q33gHS4Qk2FWEucRHMHqT69ex",
    "master_key": "r9XwzOtLCoduZgmcU27Kc0sbexW4jWTOuBHStUFb",
}

register(parse_credentials["application_id"], parse_credentials["rest_api_key"])

class Videos(Object):
    pass

class Channels(Object):
    pass

#given a tuple of values, it return them in a dictionary form
def get_dict(**kwargs):
    d= {}
    for k,v in kwargs.iteritems():
        d[k] = v
    return d

def get_channel_videos(channel_id):
    all_videos = Videos.Query.all()
    channel_videos=[]
    channel_ids=[]
    for video in all_videos:
        if video.channel == channel_id:
            #generating raw video urls from m3u8 files
            video_id = video.url.split('/')[-2]
            video.url = video.url[:-13]+video_id+'.mp4'
            channel_ids.append(video.objectId)
            channel_videos.append(video)

    return channel_videos,channel_ids

@app.route('/channels')
def channels():
    all_channels = Channels.Query.all()
    a=[]
    for i in all_channels:
        d={}
        d['name']=i.name
        d['info']=i.info
        d['channel_id']=i.objectId
        d['active_users']=randint(0,90)
        d['category'] = i.Category
        d['picture']=i.picture
        f,d['video_ids']= get_channel_videos(i.objectId)
        if i.active:
            a.append(d)

    return jsonify(data=a)


@app.route('/dash')
def dashboard():
    all_channels = Channels.Query.all()
    return flask.render_template('index.html',all_channels=all_channels)

def genFilename(filename):
    filename.replace(" ","")
    epoch = str(int(time.time()*100))
    filename=epoch+filename
    return filename

@app.route('/upload', methods=['GET','POST'])
def upload():
    all_channels = Channels.Query.all()
    
    if request.method=='GET':
        return flask.render_template('upload.html',all_channels=all_channels)

    else:
        file = request.files['file']
        channel_id=request.form['channel_id']
        video_title = request.form['title']
        if file:
            filename = genFilename(file.filename)
            filename_wext= filename.split(".")[0]
            print filename
            file.save(os.path.join('chestream_raw/', filename))
        
        os.system("ffmpeg -i chestream_raw/%s -c:v libx264 -c:a copy -b:v 192k -s 640x480 chestream_raw/192_%s"%(filename,filename))
        os.system("ffmpeg -i chestream_raw/192_%s -vf 'select=gte(n\,10)' -vframes 1 chestream_raw/thumbnail.png"%(filename))
    
        blob_service.create_container('videos', x_ms_blob_public_access='container')
    
        myvideo = open(r'chestream_raw/192_%s'%filename, 'r').read()
        mythumb = open(r'chestream_raw/thumbnail.png', 'r').read()
        blob_service.put_blob('videos', filename, myvideo, x_ms_blob_type='BlockBlob',x_ms_blob_content_type='video/mp4')
        blob_service.put_blob('videos', filename_wext+"_thumb.png", mythumb, x_ms_blob_type='BlockBlob',x_ms_blob_content_type='image/png')

        #TODO
        #upload2youtube

        try:
            u = User.signup(username='Chestream',avatar="http://i.imgur.com/nBpMmBF.png", password='12345')
        except:
            u = User.login('Chestream',"12345")
        
        video_url = "https://chestreamraw.blob.core.windows.net/videos/"+filename
        thumbnail_url = "https://chestreamraw.blob.core.windows.net/videos/%s_thumb.png"%(filename_wext)

        v = Videos(user=u,title=video_title,url=video_url,user_location="New Delhi",compiled=True,\
                video_gif="",video_thumbnail=thumbnail_url,\
                video_m3u8="",channel=channel_id,user_name="Chestream",user_avatar="http://i.imgur.com/nBpMmBF.png",\
                played=False,upvotes=randint(11,80))
        v.save()

        os.system("rm chestream_raw/*.mp4")
        os.system("rm chestream_raw/*.png")
        
        return flask.render_template('upload.html',all_channels=all_channels)


@app.route('/channel/<channel_id>')
def channel(channel_id):
    channel_videos,channel_ids= get_channel_videos(channel_id)

    channel = Channels.Query.filter(objectId=channel_id)[0]

    return flask.render_template('channel.html',channel_videos=channel_videos,channel=channel)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(debug=True,host='0.0.0.0')


