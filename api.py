#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
app = Flask(__name__)
from parse_rest.connection import register
from parse_rest.datatypes import Object, GeoPoint
from parse_rest.user import User
from flask import jsonify
import operator
import time

parse_credentials = {
    "application_id": "M5tnZk2K6PdF82Ra8485bG2VQwPjpeZLeL96VLPj",
    "rest_api_key": "VBGkzL4uHsOw0K1q33gHS4Qk2FWEucRHMHqT69ex",
    "master_key": "r9XwzOtLCoduZgmcU27Kc0sbexW4jWTOuBHStUFb",
}

register(parse_credentials["application_id"], parse_credentials["rest_api_key"])

class Videos(Object):
    pass

#given a tuple of values, it return them in a dictionary form
def get_dict(**kwargs):
    d= {}
    for k,v in kwargs.iteritems():
        d[k] = v
    return d


@app.route('/channels')
def channels():
    d= [
        {"name" : "Bhuvan Bam",
        "picture" : "https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xta1/v/t1.0-1/c22.0.160.160/p160x160/11218871_552466524895968_6251377989366115459_n.jpg?oh=36872015c678da38fc28abeb2f6e45e9&oe=5613946D&__gda__=1444496193_44f1b942badf7739e3714a3b4497b63f",
        "video_ids": ["fgqhMsk8vd","5XG2fo3FiY","SoR7E35cdK","ZsyiYMa9Ej"],
        "active_users": "90"},
        {"name" : "test",
        "picture" : "https://cdn3.iconfinder.com/data/icons/avatars-9/145/Avatar_Rabbit-128.png",
        "video_ids": ["fgqhMsk8vd","5XG2fo3FiY","SoR7E35cdK","ZsyiYMa9Ej"],
        "active_users": "10"}
    ]	

    return jsonify(data=d)

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


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

