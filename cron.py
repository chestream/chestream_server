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

def scrape_instagram(n=None):
    temp_gif = 'http://31.media.tumblr.com/a7d1b4cccb6f89dd745e88148e82b842/tumblr_mr4mswW7961sd35juo1_500.gif'
        
    #Randomly decide which API url to use
    if EPOCH%2:
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
        print video_url
        if n:
	    continue


def refresh_parse():
    all_videos = Videos.Query.all()
    for video in all_videos:
	video.upvotes=randint(10,100)
	video.played = False
        video.save()
        
def scrapeBB():
    graph_url= "https://graph.facebook.com/v2.4/BBkiVines?fields=videos&access_token=CAACEdEose0cBAA2EfmLsjyFeY7d6ZBD6XZCQ4jYJ7ZCF0fyQfdcSGLhkNg5DZBbtUxCm10Di147q7QZATRDLHBvoKhiDTIrHrfBlEfrypaUZAJSHzM6Kyz4U3exB637StZAvbY10xbAh1U5fZAYq3x2x8dyhqtO5E9DVdJWMRBk5B40JLVhMLKkJ2KpBlgNidD8dkzvvn06euS1A9meQgQhemXgKyEHlrPIZD"
    graph_url = "https://graph.facebook.com/v2.4/BBkiVines?fields=videos&access_token=CAACEdEose0cBAJRiSyhLDUDN9m1kYhjWvR7ftlX1NcJQY2Ga0AkRQuc4y1ZCMctFmcFZC4XlTDa1jBJdYbuqoXsXJeXGfDCQJPosBaGFZC6RPCbWf87DQumJRZAo5LBBf4VU7GWNDhJQmcF5uULZCsZBHkx8FrSFp9ze1Hvzb5Aj7MvZC80USMbFyx5DZBQs1eTThUoDM3FAvPJ7U83wCQWiGveY2iCXm2IZD"
    video_arr=requests.get(graph_url).json()['videos']['data']
    title_arr = []
    all_videos = Videos.Query.all()
    for video in all_videos:
        title_arr.append(video.title)
    
    for i in video_arr:
        video_id = i['id']
        video_url = "https://www.facebook.com/BBkiVines/videos/%s/?permPage=1"%video_id
        soup = BeautifulSoup(requests.get(video_url).text)
        title = soup.title.string.split('|')[0]
        print title
        if title in title_arr:
            print "Skipping repeating video: %s"%title
            continue
        os.system("mkdir %s/chestream_raw/%s"%(dir_path,video_id))
        os.system("youtube-dl %s -o '%s/chestream_raw/%%(id)s/%%(id)s.mp4'"%(video_url,dir_path))
        resp = ffmpeg("%s/chestream_raw/%s/%s.mp4"%(SERVER_URL,video_id,video_id))
        if resp!='done':
	    continue

        user_avatar = """https://fbcdn-profile-a.akamaihd.net/hprofile-ak-xta1/v/t1.0-1/c22.0.160.160/p160x160/11218871_552466524895968_6251377989366115459_n.jpg?oh=36872015c678da38fc28abeb2f6e45e9&oe=5613946D&__gda__=1444496193_44f1b942badf7739e3714a3b4497b63f"""

	try:
            u = User.signup(username='Bhuvan Bam',avatar=user_avatar, password='12345')
        except:
            u = User.login('Bhuvan Bam',"12345")
	
	video_url = "%s/chestream_raw/%s/playlist.m3u8"%(SERVER_URL,video_id)
        video_gif = "%s/chestream_raw/%s/video_teaser.gif"%(SERVER_URL,video_id)
        video_thumbnail = "%s/chestream_raw/%s/thumbnail.png"%(SERVER_URL,video_id)

        v = Videos(user=u,title=title,url=video_url,user_location="New Delhi",compiled=True,\
		video_gif=video_gif,video_thumbnail=video_thumbnail,\
		video_m3u8=video_url,user_name="Bhuvan Bam",user_avatar=user_avatar,\
		played=False,upvotes=randint(11,80))
        v.save()
        

def scrapeYoutubeChannel():
    user_avatar = 'http://i.imgur.com/KOAUTVa.png'    
    partner_name='SocioCatastrophoreTV'
    partner_username='SociaCatastrophoreTV'
    video_ids='znNwqDJACYo,scfbDJLEIGg,Vhat0nkIahw'

    title_arr = []
    all_videos = Videos.Query.all()
    for video in all_videos:
        title_arr.append(video.title)


    for video_id in video_ids.split(','):
        video_url = 'https://www.youtube.com/watch?v='+video_id
	soup = BeautifulSoup(requests.get(video_url).text)
        title = soup.title.string.split('|')[0]
        title=title.split("-")[0]
        print title
        if title in title_arr:
            print "Skipping repeating video: %s"%title
            continue
        os.system("mkdir %s/chestream_raw/%s"%(dir_path,video_id))
        os.system("youtube-dl %s -o '%s/chestream_raw/%%(id)s/%%(id)s.mp4'"%(video_url,dir_path))
        resp = ffmpeg("%s/chestream_raw/%s/%s.mp4"%(SERVER_URL,video_id,video_id))
        if resp!='done':
            continue
		
	try:
            u = User.signup(name=partner_name,username=partner_username,avatar=user_avatar, password='12345')
        except:
            u = User.login(partner_username,"12345")
	
	video_url = "%s/chestream_raw/%s/playlist.m3u8"%(SERVER_URL,video_id)
        video_gif = "%s/chestream_raw/%s/video_teaser.gif"%(SERVER_URL,video_id)
        video_thumbnail = "%s/chestream_raw/%s/thumbnail.png"%(SERVER_URL,video_id)

        v = Videos(user=u,title=title,url=video_url,user_location="New Delhi",compiled=True,\
                video_gif=video_gif,video_thumbnail=video_thumbnail,\
                video_m3u8=video_url,user_name=partner_username,user_avatar=user_avatar,\
                played=False,upvotes=randint(11,80))
        v.save()

def scrapeParseYT():
    queue_videos = Videos.Query.all()
    manual_videos = ManualVideos.Query.all()
    new_videos=[]
    title_arr = [video.title for video in queue_videos]

    for video in manual_videos:
        if video.Title not in title_arr:
            new_videos.append(video)
	    print video.Title

    for video in new_videos:
        print "Now downloading: "+ video.Title
	video_url = video.video_url
        video_id = hashlib.sha1(video_url).hexdigest()[:10]
        
        os.system("mkdir %s/chestream_raw/%s"%(dir_path,video_id))
        os.system("youtube-dl %s -o '%s/chestream_raw/%s/%s.mp4'"%(video_url,dir_path,video_id,video_id))
	print "%s/chestream_raw/%s/%s.mp4"%(SERVER_URL,video_id,video_id)
        resp = ffmpeg("%s/chestream_raw/%s/%s.mp4"%(SERVER_URL,video_id,video_id),override_length_check=True)
        if resp!='done':
            continue
        random_user = fake_users[randint(0,len(fake_users)-1)]
        name = random_user[0]
	user_name = name.replace(" ","")
	user_avatar=random_user[1]
        try:
            u = User.signup(username=user_name,name=name,avatar=user_avatar, password='12345')
        except:
            u = User.login(user_name,"12345")

        video_url = "%s/chestream_raw/%s/playlist.m3u8"%(SERVER_URL,video_id)
        video_gif = "%s/chestream_raw/%s/video_teaser.gif"%(SERVER_URL,video_id)
        video_thumbnail = "%s/chestream_raw/%s/thumbnail.png"%(SERVER_URL,video_id)

        v = Videos(user=u,title=video.Title,url=video_url,user_location="New Delhi",compiled=True,\
                video_gif=video_gif,video_thumbnail=video_thumbnail,\
                video_m3u8=video_url,user_name=user_name,user_avatar=user_avatar,\
                played=False,upvotes=randint(11,40))
        v.save()
    

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


