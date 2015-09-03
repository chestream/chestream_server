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
from cron import manual_scrape,SERVER_URL

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
        d['picture']=i.picture
        f,d['video_ids']= get_channel_videos(i.objectId)
        if i.active:
            a.append(d)

    return jsonify(data=a)

@app.route('/')
def main():
    all_videos = Videos.Query.all()
    eligible_videos = [i for i in all_videos if i.compiled and not i.played]
    max_upvotes = 0

    for i in eligible_videos:
        if i.upvotes > max_upvotes:
            alpha_video = i
            max_upvotes = i.upvotes

    if not alpha_video:
        return
    av = alpha_video
    video_data = get_dict(title=av.title,\
    	video_id=av.objectId,\
	video_gif=av.video_gif,\
    	url = av.url,\
    	video_m3u8=av.video_m3u8,\
    	user_location=av.user_location,\
    	time_ago='14 minutes ago',\
    	#user=av.user,\
    	play_epoch=int(time.time()) + 10
    )

    return jsonify(data=video_data)

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
        if file:
            filename = genFilename(file.filename)
            print filename
            file.save(os.path.join('chestream_raw/', filename))

        flash('File was successfully uploaded')
        manual_scrape("%s/chestream_raw/%s"%(SERVER_URL,filename),'Test title',channel_id=channel_id)
        return flask.redirect("%s/chestream_raw/%s"%(SERVER_URL,filename.split('.')[0]))


@app.route('/channel/<channel_id>')
def channel(channel_id):
    channel_videos,channel_ids= get_channel_videos(channel_id)

    channel = Channels.Query.filter(objectId=channel_id)[0]

    return flask.render_template('channel.html',channel_videos=channel_videos,channel=channel)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True,host='0.0.0.0')

