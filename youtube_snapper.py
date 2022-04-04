import time
import os
import argparse
import pytube
import urllib.request


doc = """
youtube_snapper.py module
---------------------------------------------------------------------

REQUIREMENTS TO RUN THIS MODULE:
- pytube installed (pip install pytube, reinstall if error to fix bug)
- ffmpeg.exe has to be in the same directory as this module
  or the relative path must be set manually in FF_PATH.

Documentation of the pytube module:
    https://pytube.io/en/latest/api.html#stream-object

Usage examples of this module:
>>> youtube_snapper.py -v "VidLink1" "VidLink2" "VidLink3" --hq --mkv
>>> youtube_snapper.py -p "Playlistlink" --mp3
>>> youtube_snapper.py -f "Filelink"

---------------------------------------------------------------------
"""

# relative path for ffmpeg.exe.
# Leave empty if ffmpeg was added to PATH
FF_PATH = ""

# relative path to where downloaded material is placed
DL_PATH = "./downloads"

RESOLUTIONS = ["2160p", "1440p", "1080p", "720p", "480p",
               "360p", "240p", "144p"]


def convert_title(title: str) -> str:
    """
        Removes characters from the given string that are not permitted to
        appear in file names.
    """
    for c in ("<", ">", ":", "\"", "/", "\\", "|", "?", "*"):
        title = title.replace(c, " ")
    return title


def download_iterator(url_list, to_call):
    """
        Handles downloads of multiple objects.
    """
    failed = []
    to_download = url_list.copy()
    while True:
        for video_url in to_download:
            try:
                print("-" * 15)
                to_call(video_url)
            except Exception as e:
                print("Failed a video. Trying again.")
                print(e)
                failed.append(video_url)
            else:
                print("Success.")
        if failed:
            to_download = failed
            failed = []
        else:
            break


def download_video(video_url):
    """
        Downloads the video at the specified video_url by finding the
        best video stream by resolution, fps and codec and the best
        audio stream by abr seperately and combining them using ffmpeg
        Default filetype is mp4.
    """
    try:
        youtube = pytube.YouTube(video_url,
                                 on_progress_callback=download_callback)
    except Exception:
        print(f"[ERROR] Could not load {video_url}")
        time.sleep(2)
        return False

    if not args.mkv:
        # get thumbnail
        urllib.request.urlretrieve(youtube.thumbnail_url, "thumb.jpg")

    iter_res = iter(RESOLUTIONS[2 * (1 - args.hq):])
    while True:
        try:
            video = youtube.streams.filter(res=next(iter_res))
        except StopIteration:
            video = youtube.streams.get_highest_resolution()
            break
        if video:
            if video.filter(video_codec="vp9"):
                video = video.filter(video_codec="vp9")
            video = video.order_by("fps").last()
            break

    print(f"title={video.title}")
    print(f"res={video.resolution}, fps={video.fps}, "
          f"filetype={video.subtype}, video_codec={video.video_codec}")

    video_filetype = video.mime_type.split("/")[-1]
    vid_title = convert_title(video.title)

    if video.includes_video_track:
        audio = youtube.streams.filter(only_audio=True).order_by("abr").last()
        audio_filetype = audio.mime_type.split("/")[-1]

        print(f"abr={audio.abr}, filetype={audio.subtype}, "
              f"audio_codec={audio.audio_codec}")

        video.download(filename=(f"tempvid.{video_filetype}"))
        audio.download(filename=(f"tempaud.{audio_filetype}"))

        if args.mkv:
            os.system(FF_PATH + "ffmpeg -hide_banner -loglevel warning -stats"
                      " -i tempvid.{} -i tempaud.{} -c "
                      "copy \"{}\".mkv".format(video_filetype,
                                               audio_filetype, vid_title))
        else:  # args.mp4
            os.system(FF_PATH + "ffmpeg -hide_banner -loglevel warning "
                      "-stats -i tempvid.{} -i tempaud.{} -i thumb.jpg"
                      " -map 0 -map 1 -map 2 -c:v copy -c:a aac "
                      "-disposition:2 attached_pic \"{}\".mp4"
                      .format(video_filetype, audio_filetype, vid_title))
            os.system(f"del thumb.jpg")

        os.system(f"del tempvid.{video_filetype}")
        os.system(f"del tempaud.{audio_filetype}")

    else:
        print("Downloading video and audio...")
        video.download(filename=(f"\"{vid_title}\".{video_filetype}"))

    return True


def download_sound(video_url):
    """
        Downloads the video sound at the specified video_url by finding the
        the best audio stream by abr. Default filetype is mp3.
    """
    try:
        youtube = pytube.YouTube(video_url,
                                 on_progress_callback=download_callback)
    except Exception:
        print(f"[ERROR] Could not load {video_url}")
        time.sleep(2)
        return False

    audio = youtube.streams.filter(only_audio=True).order_by("abr").last()
    audio_filetype = audio.mime_type.split("/")[-1]

    vid_title = audio.title

    for c in ("<", ">", ":", "\"", "/", "\\", "|", "?", "*"):
        vid_title = vid_title.replace(c, " ")

    print(f"abr={audio.abr}, filetype={audio.subtype}, "
          f"audio_codec={audio.audio_codec}")

    audio.download(filename=(f"tempaud.{audio_filetype}"))

    os.system(FF_PATH + f"ffmpeg -hide_banner -loglevel warning -stats "
              f"-i tempaud.{audio_filetype} -acodec"
              f" libmp3lame \"{vid_title}\".mp3")

    os.system(f"del tempaud.{audio_filetype}")

    return True


def download_callback(self, chunk, bytes_remaining):
    bytes_downloaded = self.filesize - bytes_remaining
    percent = bytes_downloaded / self.filesize * 100
    print(f"Downloading... {int(percent)}%" + " " * 3, end="\r")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument("-video", "-v", type=str, nargs='+',
                   metavar="VIDEO_URL", help="Downloads the video at "
                   "the specified youtube-video-url")
    g.add_argument("-playlist", "-p", type=str, metavar="PLAYLIST_URL",
                   help="Downloads all videos in the specified playlist")
    g.add_argument("-file", "-f", type=str, metavar="FILE_PATH",
                   help="Downloads all urls specified in textfile"
                   " (seperated by new line)")
    parser.add_argument("-hq", action="store_true",
                        help="Allows resolutions > 1080p")
    h = parser.add_mutually_exclusive_group()
    h.add_argument("-mkv", action="store_true",
                   help="Specifies output file to be of type mkv")
    h.add_argument("-mp3", action="store_true",
                   help="Specifies output file to be of type mp3")
    args = parser.parse_args()

    download = download_sound if args.mp3 else download_video

    if args.video:
        os.chdir(DL_PATH)
        download_iterator(args.video, download)
    elif args.playlist:
        playlist = pytube.Playlist(args.playlist)
        os.chdir(DL_PATH + "/" + convert_title(playlist.title))
        download_iterator(playlist.video_urls, download)
    elif args.file:
        os.chdir(DL_PATH + "/" + args.file[:args.file.rfind(".")])
        with open(args.file, "r") as f:
            links = list(map(str.strip, f.readlines()))
        download_iterator(links, download)
    else:
        print(doc, end="\n"*2)
        parser.print_help()
