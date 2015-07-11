# chestream_server

+ Converting mp4 to .ts
  + ffmpeg -i input.mp4 -c copy -bsf h264_mp4toannexb output.ts

+ Split .ts files into many segments
  + ffprobe -show_frames output.ts -print_format json > foo.txt

+ Splitting BIG .ts file into chunks
  + ffmpeg -loglevel quiet  -i BIGFILE.ogv -f mpegts - | m3u8-segmenter -i - -d 10 -p tmp/big_buck_bunny -m tmp/big_buck.m3u8 -u http://mydomain.com


##Resources
+ HD videos for testing 
  + http://www.highdefforum.com/high-definition-movies-video-clips/6537-official-hd-video-clip-list.html

+ Download segmenter from here
  + http://svn.assembla.com/svn/legend/segmenter/segmenter.c

+ Build it
  + gcc -Wall -g segmenter.c -o segmenter -lavformat -lavcodec -lavutil -lbz2 -lm -lz -lfaac -lmp3lame -lx264 -lfaad

+ It might throw an error
  + segmenter.c:21:34: fatal error: libavformat/avformat.h: No such file or directory

+ Install dependencies
  + sudo apt-get install libavformat53 libavformat-dev libavcodec53

+ Building ffmpeg from source 
  + https://gist.github.com/faleev/3435377

+ How to install libfaac-dev 
  + http://superuser.com/questions/467774/how-to-install-libfaac-dev

+ Unofficial fork of m3u8 segmenter, which is currently deployed on the server
  + https://github.com/johnf/m3u8-segmenter

http://i.imgur.com/Zr1rPt7.gif
http://www.ioncannon.net/programming/452/iphone-http-streaming-with-ffmpeg-and-an-open-source-segmenter/


###Server stuff

+ nginx logs | tail -f /opt/nginx/logs/error.log
+ restarting nginx
  + cd /usr/sbin/ | ./nginx -s reload
  + 


