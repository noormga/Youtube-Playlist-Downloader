import os
os.system("")  # enables ansi escape characters in terminal
import googleapiclient.discovery
import googleapiclient.errors
from pytube import YouTube
#from pytube.cli import on_progress
#,on_progress_callback=on_progress * add behind yt = YouTube(f"https://www.youtube.com/watch?v={video.urlId}" *
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
channelId = config['personal']['channelId']
path = config['personal']['path']

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

unallowedCharacters = [':','*','"','<','>','|','\\','/','?',"'"]

red = "\033[1;31m"
blue = "\033[1;34m"
green = "\033[1;32m"
magenta = "\033[1;35m"
closeEscape = "\033[0m"

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    global youtube
    youtube = googleapiclient.discovery.build(
               api_service_name, 
               api_version, 
               developerKey='TOKEN')

    request = youtube.playlists().list(
        part="snippet",
        channelId=channelId,
        maxResults=50
    )
    global response
    response = request.execute()

def get_playlists():
    playlists = []

    class Playlist:
        def __init__(self, title, id, videos):
            self.title = title
            self.id = id
            self.videos = videos
        def __repr__(self):
            return repr((self.title, self.id, self.videos))

    global response
    while "nextPageToken" in response:
        for i in range(len(response["items"])):
            playlists.append(Playlist(response["items"][i]["snippet"]["title"], response["items"][i]["id"], get_videos(response["items"][i]["id"])))

        request = youtube.playlists().list(
            part="snippet",
            channelId=channelId,
            maxResults=50,
            pageToken=response["nextPageToken"]
        )
        response = request.execute()
    else:
        for i in range(len(response["items"])):
            playlists.append(Playlist(response["items"][i]["snippet"]["title"], response["items"][i]["id"], get_videos(response["items"][i]["id"])))

    return playlists

def get_videos(playlistId):
    videos = []

    class Video:
        def __init__(self, title, urlId):
            self.title = title
            self.urlId = urlId
        def __repr__(self):
            return repr((self.title, self.urlId))

    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        playlistId=playlistId
    )
    response = request.execute()

    while "nextPageToken" in response:
        for i in range(len(response["items"])):
            videos.append(Video(response["items"][i]["snippet"]["title"], response["items"][i]["snippet"]["resourceId"]["videoId"]))

        request = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,
        playlistId=playlistId,
        pageToken=response["nextPageToken"]
        )
        response = request.execute()
    else:
        for i in range(len(response["items"])):
            videos.append(Video(response["items"][i]["snippet"]["title"], response["items"][i]["snippet"]["resourceId"]["videoId"]))

    return videos

def downloader(video, playlistPath, playlistTitle):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video.urlId}")
        video = yt.streams.get_audio_only()
        out_file = video.download(output_path=playlistPath)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        print(f"{green}Added {magenta}{video.title}{green} to {blue}{playlistTitle}{closeEscape}")
    except:
        print(f"{red} Unavailable video in {blue}{playlistTitle}{closeEscape}\n")

def console():
    for playlist in playlists:
        playlistPath = path + "/" + playlist.title
        if not os.path.exists(playlistPath):
            os.mkdir(path + "/" + playlist.title)
            print(f"\n{green}Adding playlist {blue}{playlist.title}{closeEscape}\n")
            for video in playlist.videos:
                downloader(video, playlistPath, playlist.title)
            print("\n")
        else:
            for video in playlist.videos:
                for unallowedCharacter in unallowedCharacters:
                    video.title = video.title.replace(unallowedCharacter, '')
                if not os.path.exists(f"{playlistPath}/{video.title}.mp3"):
                    downloader(video, playlistPath, playlist.title)
            print("\n")

main()
playlists = get_playlists()
console()
print("\n")
os.system('pause')