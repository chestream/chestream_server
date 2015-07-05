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

MIN_LENGTH=10

dir_path = os.path.dirname(os.path.abspath(__file__))

parse_credentials = {
    "application_id": "M5tnZk2K6PdF82Ra8485bG2VQwPjpeZLeL96VLPj",
    "rest_api_key": "VBGkzL4uHsOw0K1q33gHS4Qk2FWEucRHMHqT69ex",
    "master_key": "r9XwzOtLCoduZgmcU27Kc0sbexW4jWTOuBHStUFb",
}

register(parse_credentials["application_id"], parse_credentials["rest_api_key"])

class Videos(Object):
    pass

con = pycps.Connection('tcp://cloud-eu-0.clusterpoint.com:9007', 'chestream', 'stomatrix@gmail.com', 'sauravclusterpoint', '1104')
blob_service = BlobService(account_name='fo0', account_key='4QX9QsqElWP0Z9KsUWmzpM5tsM1L565VzzZvZxh9qefM6hbOj/ex1Z+0NwZUURnweimZZgzVGe6vAeytDqkVLg==')
base_url="https://fo0.blob.core.windows.net/videos/"


#given a tuple of values, it return them in a dictionary form
def get_dict(**kwargs):
    d= {}
    for k,v in kwargs.iteritems():
        d[k] = v
    return d


def test_upload():
    blob_service.put_block_blob_from_path(
        'fo0',
        'videos',
        '/home/saurav/Desktop/sean1.png',
        x_ms_blob_content_type='image/png'
    )


def get_azure_list():
    blobs = blob_service.list_blobs('videos')
    arr = []
    for blob in blobs:
        arr.append(blob.name)
    return arr
    


def get_clusterpoint():
    resp = con.status()
    #print("Processed in {0}; dump:\n{1}". format(resp.seconds, resp.status))
    resp = con.retrieve_last(docs=10, offset=0)
    arr = []
    for id, document in resp.get_documents().items():
        arr.append(id)
    return arr

    
def push_clusterpoint():
    a=con.insert({'video_1234132': {'video_title': 'Loerem Ipsum', 'video_upvotes': '100',\
        'video_m3u8':'http://128.199.128.227/chestream/video_1234132/playlist.m3u8',\
        'user_name':'saurav',\
        'user_location':'India',\
        'user_avatar':'',\
        'video_title':'My holidays in bahamas',\
        'video_played':'false',\
        'video_compiled':'false',\
        'video_url':'https://fo0.blob.core.windows.net/videos/video_1434736266.mp4',\
        'video_teaser':'http://128.199.128.227/chestream/video_1234132/video.gif'}})
    print a,dir(a)


def update_clusterpoint(video_name,video_compiled,video_m3u8,video_teaser):
    a=con.retrieve(video_name)
    for id, document in a.get_documents().items():
        doc = document

    doc['video_compiled']='true'
    doc['video_m3u8']=video_m3u8
    doc['video_teaser']=video_teaser

    con.update({video_name:doc})

def update_parse(objectId,video_m3u8,video_gif):
    #v = Videos.Query.filter(objectId=objectId)
    v = Videos(objectId=objectId,video_m3u8=video_m3u8,video_gif=video_gif,compiled=True)
    v.save()
    


def ffmpeg(video_url):
    video_name = video_url.split('/')[-1]
    video_name=video_name.split('.')[0]
    print video_name

    print "making directory chestream_raw/%s"%video_name
    os.system("mkdir %s/chestream_raw/%s/"%(dir_path,video_name))
    
    print "downloading video file"
    os.system("wget %s -P %s"%(video_url,dir_path))

    print "Checking length of video file"
    answer = os.popen("%s/get_duration.sh %s/%s.mp4"%(dir_path,dir_path,video_name))
    length = answer.readlines()[0].strip()
    if int(length) < MIN_LENGTH:
        print "Skipping video, length too low"
        return

    print "compiling .ts files and generating m3u8"
    if 'https://fo0.blob.core.windows.net' in video_url:
        cmd = "ffmpeg -v 9 -loglevel quiet -re -i %s/%s.mp4 -an -c:v libx264 -b:v 512k -flags -global_header -map 0 -f segment -segment_time 4 \
        -segment_list_entry_prefix http://128.199.128.227/chestream_raw/%s/ -segment_list %s/chestream_raw/%s/playlist.m3u8 \
        -segment_format mpegts %s/chestream_raw/%s/part%%05d.ts"%(dir_path,video_name,dir_path,video_name,video_name,dir_path,video_name)
    else:
	#it's an instagram video
        cmd = "ffmpeg -v 9 -loglevel quiet -re -i %s/%s.mp4 -an -c:v libx264 -b:v 512k -flags -global_header -f segment -segment_time 4 \
        -segment_list_entry_prefix http://128.199.128.227/chestream_raw/%s/ -segment_list %s/chestream_raw/%s/playlist.m3u8 \
        -segment_format mpegts %s/chestream_raw/%s/part%%05d.ts"%(dir_path,video_name,video_name,dir_path,video_name,dir_path,video_name)
    
    os.system(cmd)
    os.system("cp %s/%s.mp4 %s/chestream_raw/%s/"%(dir_path,video_name,dir_path,video_name))
    
    print "Generating Gif"
    gif_cmd = "ffmpeg -y -ss 3 -t 3 -i %s/%s.mp4 -vf fps=10,scale=320:-1:flags=lanczos,palettegen %s/palette.png"%(dir_path,video_name,dir_path)
    gif_cmd2 = 'ffmpeg -ss 3 -t 3 -i %s/%s.mp4 -i %s/palette.png -filter_complex \
            "fps=10,scale=320:-1:flags=lanczos[x];[x][1:v]paletteuse" %s/chestream_raw/%s/video_teaser.gif'%(dir_path,video_name,dir_path,dir_path,video_name)
    
    os.system(gif_cmd)
    os.system(gif_cmd2)
    os.system("rm %s/%s.mp4"%(dir_path,video_name))


def main(n=None):
    all_videos = Videos.Query.all()
    new_videos = [i for i in all_videos if not i.compiled]
    
    for video in new_videos[:n]:
        video_name = video.url.split('/')[-1]
        video_name = video_name.split('.')[0]
        video_compiled='true'
        video_m3u8='http://128.199.128.227/chestream_raw/%s/playlist.m3u8'%video_name
        video_gif ='http://128.199.128.227/chestream_raw/%s/video_teaser.gif'%video_name
        ffmpeg(video.url)
	try:
            ret = urllib2.urlopen(video_m3u8)
	    ret2 = urllib2.urlopen(video_gif)
	except:
	    print "meta files not created: Skipping"
	    continue
	update_parse(video.objectId,video_m3u8,video_gif)

def get_location(lat,long):
    return "New Delhi"

def scrape_instagram(n=None):
    temp_gif = 'http://31.media.tumblr.com/a7d1b4cccb6f89dd745e88148e82b842/tumblr_mr4mswW7961sd35juo1_500.gif'
    
    #Randomly decide which API url to use
    if int(time.time())%2:
        url = "https://api.instagram.com/v1/media/popular?access_token=362670545.1677ed0.87ca9b1581b44617b6154a213c0d8c2d"
    else:
        url = "https://api.instagram.com/v1/tags/hyperlapse/media/recent?access_token=362670545.1677ed0.87ca9b1581b44617b6154a213c0d8c2d"
   
    j = requests.get(url).json()
    videos = [i for i in j['data'] if i['type'] == 'video']
    
    all_videos = Videos.Query.all()
    all_video_urls = [i.url for i in all_videos ]

    for i in videos:
        username = i['user']['full_name'].encode('ascii','ignore')
        title = i['caption']['text'].encode('ascii','ignore')
        video_url = i['videos']['standard_resolution']['url']
        video_name = video_url.split('/')[-1]        

	print "downloading video file"
        os.system("wget %s -P %s"%(video_url,dir_path))
        
        print "Checking length of video file"
        answer = os.popen("%s/get_duration.sh %s/%s"%(dir_path,dir_path,video_name))
	length = answer.readlines()[0].strip()
	os.system("rm %s/%s"%(dir_path,video_name))	
	print length

        if int(length) < MIN_LENGTH:
            print "Skipping video, length too low"
            continue 

        if video_url in all_video_urls:
            print "Repeat Video: ignoring"
            continue

        print title
        if len(title) > 60:
            title = title[:55] + " ..."

        time = i['created_time']
        user_avatar = i['user']['profile_picture']
        likes = i['likes']['count']

        try:
            user_location=get_location(i['location']['latitude'],i['location']['longitude'])
        except TypeError:
            try:
                user_location=i['location']['name']
            except:
                user_location="New Delhi"
        
        try:
            u = User.signup(username=username,avatar=user_avatar, password="12345")
        except:
            try:
            	u = User.login(username,"12345")
	    except:
                print "login failure"
		break

        v = Videos(user=u,title=title,url=video_url,user_location=user_location,compiled=False,played=False,upvotes=likes/100,video_gif=temp_gif)
        v.save()
        if n:
	    continue


def refresh_parse():
    all_videos = Videos.Query.all()
    for video in all_videos:
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

