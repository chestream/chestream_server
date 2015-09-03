

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
        

def scrapelaf():
    title_arr = []
    all_videos = Videos.Query.all()
    for video in all_videos:
        title_arr.append(video.title)

    video_ids='kd4xDp8rkGk,DJrOH3A1WNQ,JjsBIhgI8Y'
    for video_id in video_ids.split(','):
        video_url = 'https://www.youtube.com/watch?v='+video_id
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
	user_avatar="https://medium2.global.ssl.fastly.net/max/800/1*EBwpIpWBSkeIJMBrwCfoFA.jpeg"	
	try:
            u = User.signup(username='Little Anarky Films',avatar=user_avatar, password='12345')
        except:
            u = User.login('Little Anarky Films',"12345")
	
	video_url = "%s/chestream_raw/%s/playlist.m3u8"%(SERVER_URL,video_id)
        video_gif = "%s/chestream_raw/%s/video_teaser.gif"%(SERVER_URL,video_id)
        video_thumbnail = "%s/chestream_raw/%s/thumbnail.png"%(SERVER_URL,video_id)

        v = Videos(user=u,title=title,url=video_url,user_location="New Delhi",compiled=True,\
                video_gif=video_gif,video_thumbnail=video_thumbnail,\
                video_m3u8=video_url,user_name="Little Anarky Films",user_avatar=user_avatar,\
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
        video_url = video.video_url
        video_id = hashlib.sha1(video_url).hexdigest()[:10]
        
        os.system("mkdir %s/chestream_raw/%s"%(dir_path,video_id))
        os.system("youtube-dl %s -o '%s/chestream_raw/%%(id)s/%%(id)s.mp4'"%(video_url,dir_path))
        resp = ffmpeg("%s/chestream_raw/%s/%s.mp4"%(SERVER_URL,video_id,video_id))
        if resp!='done':
            continue
        random_user = fake_users[randint(0,len(fake_users)-1)]
        user_name = random_user[0]
	user_avatar=random_user[1]
        try:
            u = User.signup(username=user_name,avatar=user_avatar, password='12345')
        except:
            u = User.login(user_name,"12345")

        video_url = "%s/chestream_raw/%s/playlist.m3u8"%(SERVER_URL,video_id)
        video_gif = "%s/chestream_raw/%s/video_teaser.gif"%(SERVER_URL,video_id)
        video_thumbnail = "%s/chestream_raw/%s/thumbnail.png"%(SERVER_URL,video_id)

        v = Videos(user=u,title=title,url=video_url,user_location="New Delhi",compiled=True,\
                video_gif=video_gif,video_thumbnail=video_thumbnail,\
                video_m3u8=video_url,user_name="Little Anarky Films",user_avatar=user_avatar,\
                played=False,upvotes=randint(11,80))
        v.save()
	break
    


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
