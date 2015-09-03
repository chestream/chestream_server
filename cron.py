#!/usr/bin/env python
# -*- coding: utf-8 -*-

from azure.storage import BlobService
import pycps
import os
import requests
from parse_rest.connection import register
from parse_rest.datatypes import Object, GeoPoint
from parse_rest.user import User
import sys
import urllib2
import time
from bs4 import BeautifulSoup
from random import randint
import hashlib
import time


MIN_LENGTH=10
EPOCH = int(time.time())
SERVER_URL = 'http://104.131.207.33'

dir_path = os.path.dirname(os.path.abspath(__file__))

parse_credentials = {
    "application_id": "M5tnZk2K6PdF82Ra8485bG2VQwPjpeZLeL96VLPj",
    "rest_api_key": "VBGkzL4uHsOw0K1q33gHS4Qk2FWEucRHMHqT69ex",
    "master_key": "r9XwzOtLCoduZgmcU27Kc0sbexW4jWTOuBHStUFb",
}

register(parse_credentials["application_id"], parse_credentials["rest_api_key"])

class Videos(Object):
    pass

class ManualVideos(Object):
    pass

con = pycps.Connection('tcp://cloud-eu-0.clusterpoint.com:9007', 'chestream', 'stomatrix@gmail.com', 'sauravclusterpoint', '1104')
blob_service = BlobService(account_name='fo0', account_key='4QX9QsqElWP0Z9KsUWmzpM5tsM1L565VzzZvZxh9qefM6hbOj/ex1Z+0NwZUURnweimZZgzVGe6vAeytDqkVLg==')
base_url="https://fo0.blob.core.windows.net/videos/"

fake_users = [
    ["Faisal","http://i.imgur.com/RofSvsa.png"],
    ["Crime Master Gogo","http://i.imgur.com/JV60lE2.png"],
    ["Gabbar Singh","http://i.imgur.com/SPJHTUb.png"],
    ["Marla Singer","http://i.imgur.com/NiRv6gG.png"],
    ["Darth Vader","http://i.imgur.com/vAJFuzL.png"],
    ["Tony Montana","http://i.imgur.com/aS1tmbB.png"],
    ["Jack Sparrow","http://i.imgur.com/Ahx14o6.png"]
]

#given a tuple of values, it return them in a dictionary form
def get_dict(**kwargs):
    d= {}
    for k,v in kwargs.iteritems():
        d[k] = v
    return d


def update_parse(objectId,video_m3u8,video_gif,video_thumbnail):
    #v = Videos.Query.filter(objectId=objectId)
    try:
        user_name = video.user.username
        user_avatar = video.user.avatar
    except:
        user_name = 'test'
        user_avatar = 'https://i.imgur.com/4VjEHoK.jpg'

    v = Videos(objectId=objectId,video_m3u8=video_m3u8,video_gif=video_gif,video_thumbnail=video_thumbnail,\
	user_name=user_name,user_avatar=user_avatar,compiled=True)
    v.save()
    

def ffmpeg(video_url,override_length_check=False):
    video_name = video_url.split('/')[-1]
    video_name=video_name.split('.')[0]
    print video_name

    print "making directory chestream_raw/%s"%video_name
    os.system("mkdir %s/chestream_raw/%s/"%(dir_path,video_name))
    
    print "downloading video file"
    os.system("wget %s -P %s"%(video_url,dir_path))
    
    if not override_length_check:
        print "Checking length of video file"
        answer = os.popen("%s/get_duration.sh %s/%s.mp4"%(dir_path,dir_path,video_name))
        length = answer.readlines()[0].strip()
        if int(length) < MIN_LENGTH:
            print "Skipping video, length too low"
            return ""

    print "compiling .ts files and generating m3u8"
    if 'https://fo0.blob.core.windows.net' in video_url:
        cmd = "ffmpeg -v 9 -loglevel quiet -re -i %s/%s.mp4 -c:v libx264 -c:a copy -b:v 512k -flags -global_header -map 0 -f segment -segment_time 4 \
        -segment_list_entry_prefix %s/chestream_raw/%s/ -segment_list %s/chestream_raw/%s/playlist.m3u8 \
        -segment_format mpegts %s/chestream_raw/%s/part%%05d.ts"%(dir_path,video_name,SERVER_URL,dir_path,video_name,video_name,dir_path,video_name)
    else:
	#it's an instagram video
        cmd = "ffmpeg -v 9 -loglevel quiet -re -i %s/%s.mp4 -c:v libx264 -c:a copy -b:v 512k -flags -global_header -f segment -segment_time 4 \
        -segment_list_entry_prefix %s/chestream_raw/%s/ -segment_list %s/chestream_raw/%s/playlist.m3u8 \
        -segment_format mpegts %s/chestream_raw/%s/part%%05d.ts"%(dir_path,video_name,SERVER_URL,video_name,dir_path,video_name,dir_path,video_name)
    
    os.system(cmd)
    
    print "Generating Gif"
    gif_cmd = "ffmpeg -y -ss 3 -t 3 -i %s/%s.mp4 -vf fps=10,scale=320:-1:flags=lanczos,palettegen %s/palette.png"%(dir_path,video_name,dir_path)
    gif_cmd2 = 'ffmpeg -ss 3 -t 3 -i %s/%s.mp4 -i %s/palette.png -filter_complex \
            "fps=10,scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse" %s/chestream_raw/%s/video_teaser.gif'%(dir_path,video_name,dir_path,dir_path,video_name)
    
    print "Generating vide thumbnail"
    frame_cmd ="ffmpeg -i %s/%s.mp4 -vf 'select=gte(n\,10)' -vframes 1 %s/chestream_raw/%s/thumbnail.png"%(dir_path,video_name,dir_path,video_name)

    os.system(gif_cmd)
    os.system(gif_cmd2)
    os.system(frame_cmd)

    os.system("cp %s/%s.mp4 %s/chestream_raw/%s/"%(dir_path,video_name,dir_path,video_name))
    os.system("rm %s/%s.mp4"%(dir_path,video_name))
    return "done"

def manual_scrape(video_url,title):
    video_name = video_url.split('/')[-1]
    video_name = video_name.split('.')[0]
    video_compiled='true'
    video_m3u8='%s/chestream_raw/%s/playlist.m3u8'%(SERVER_URL,video_name)
    video_gif ='%s/chestream_raw/%s/video_teaser.gif'%(SERVER_URL,video_name)
    video_thumbnail ='%s/chestream_raw/%s/thumbnail.png'%(SERVER_URL,video_name)
    ffmpeg(video_url)
    try:
        u = User.signup(username='Chestream',avatar="http://i.imgur.com/nBpMmBF.png", password='12345')
    except:
        u = User.login('Chestream',"12345")
    v = Videos(user=u,title=title,url=video_url,user_location="New Delhi",compiled=True,\
                video_gif=video_gif,video_thumbnail=video_thumbnail,\
                video_m3u8=video_m3u8,user_name="Chestream",user_avatar="http://i.imgur.com/nBpMmBF.png",\
                played=False,upvotes=randint(11,80))
    v.save()
    #update_parse(video.objectId,video_m3u8,video_gif,video_thumbnail)

def main(n=None):
    all_videos = Videos.Query.all()
    new_videos = [i for i in all_videos if not i.compiled]
    
    for video in new_videos[:n]:
        video_name = video.url.split('/')[-1]
        video_name = video_name.split('.')[0]
        video_compiled='true'
        video_m3u8='%s/chestream_raw/%s/playlist.m3u8'%(SERVER_URL,video_name)
        video_gif ='%s/chestream_raw/%s/video_teaser.gif'%(SERVER_URL,video_name)
        video_thumbnail ='%s/chestream_raw/%s/thumbnail.png'%(SERVER_URL,video_name)
        ffmpeg(video.url)
	try:
            ret = urllib2.urlopen(video_m3u8)
	    ret2 = urllib2.urlopen(video_gif)
	except:
	    print "meta files not created: Skipping"
	    continue
	update_parse(video.objectId,video_m3u8,video_gif,video_thumbnail)

def get_location(lat,long):
    return "New Delhi"


def refresh_parse():
    all_videos = Videos.Query.all()
    for video in all_videos:
	video.upvotes=randint(10,100)
	video.played = False
        video.save()


if __name__ == '__main__':
    if 'refresh' == sys.argv[1]:
        print "Refreshing parse list"
        refresh_parse()

    elif 'main' == sys.argv[1]:
        print 'Running main function'
        main()

    elif 'instagram' == sys.argv[1]:
        print "Scraping Instagram"
        scrape_instagram()

    elif 'testagram' == sys.argv[1]:
        scrape_instagram(n=1)
        main(n=1)

    elif 'test' == sys.argv[1]:
        manual_scrape("http://104.131.207.33/chestream_raw/gujj3.mp4","Gujarat Riots")

    elif 'scrapeParse' == sys.argv[1]:
	scrapeParseYT()


