"""
youtube_snapper.py module
---------------------------------------------------------------------

PLEASE CHECK YOUTUBE'S TERMS OF SERVICE BEFORE USING THIS TOOL

REQUIREMENTS TO RUN THIS MODULE:
- pytube installed (pip install pytube, reinstall if error to fix bug)
- ffmpeg.exe has to be in the same directory as this module
  (or the relative path must be set manually in FF_PATH).

Documentation of the pytube module:
    https://pytube.io/en/latest/api.html#stream-object

Usage examples of this module:
>>> youtube_snapper.py -v "VidLink1" "VidLink2" "VidLink3" -q 1440p --mkv
>>> youtube_snapper.py -p "Playlistlink" --mp3
>>> youtube_snapper.py -f "Filelink"

---------------------------------------------------------------------
"""


import logging
import time
import os
import argparse
import pytube
import urllib.request
import re
import traceback


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
    max_retry = 3
    to_download = url_list.copy()
    while max_retry > 0:
        for video_url in to_download:
            try:
                to_call(video_url)
            except Exception:
                logging.error(f"""Failed to download {video_url}."""
                              """ Trying again in 5 seconds...""")
                logging.debug(traceback.format_exc())
                failed.append(video_url)
                time.sleep(1)
        if failed:
            to_download = failed
            failed = []
            max_retry -= 1
        else:
            break
    else:
        logging.critical("""Aborting download after multiple"""
                         """ conesecutive fails.""")


def download_video(video_url):
    """
        Downloads the video at the specified video_url by finding the
        best video stream by resolution, fps and codec and the best
        audio stream by abr seperately and combining them using ffmpeg
        Default filetype is mp4.
    """
    # youtube = pytube.YouTube(video_url,
    #                         on_progress_callback=download_callback)

    youtube = pytube.YouTube(video_url, use_oauth=False, allow_oauth_cache=False,
                             on_progress_callback=download_callback)

    if not args.mkv:
        # get thumbnail
        urllib.request.urlretrieve(youtube.thumbnail_url, "thumb.jpg")

    iter_res = filter(lambda x: int(x[:-1]) <= args.quality, RESOLUTIONS)

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

    logging.info(f"title={video.title}")
    logging.info(f"video_res={video.resolution}")
    logging.info(f"video_fps={video.fps}")
    logging.info(f"video_filetype={video.subtype}")
    logging.info(f"video_codec={video.video_codec}")

    video_filetype = video.mime_type.split("/")[-1]
    vid_title = convert_title(video.title)

    if video.includes_video_track:
        audio = youtube.streams.filter(only_audio=True).order_by("abr").last()
        audio_filetype = audio.mime_type.split("/")[-1]

        logging.info(f"audio_abr={audio.abr}")
        logging.info(f"audio_filetype={audio.subtype}")
        logging.info(f"audio_codec={audio.audio_codec}")

        video.download(filename=(f"tempvid.{video_filetype}"))
        audio.download(filename=(f"tempaud.{audio_filetype}"))

        logging.info("Merging temp files using FFMpeg...")

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
            os.system("del thumb.jpg")

        os.system(f"del tempvid.{video_filetype}")
        os.system(f"del tempaud.{audio_filetype}")

    else:
        logging.info("Downloading video and audio...")
        video.download(filename=(f"\"{vid_title}\".{video_filetype}"))


def download_sound(video_url):
    """
        Downloads the video sound at the specified video_url by finding the
        the best audio stream by abr. Default filetype is mp3.
    """
    # youtube = pytube.YouTube(video_url,
    #                        on_progress_callback=download_callback)

    youtube = pytube.YouTube(video_url, use_oauth=True, allow_oauth_cache=True,
                             on_progress_callback=download_callback)

    audio = youtube.streams.filter(only_audio=True).order_by("abr").last()
    audio_filetype = audio.mime_type.split("/")[-1]

    vid_title = convert_title(audio.title)

    logging.info(f"audio_abr={audio.abr}")
    logging.info(f"audio_filetype={audio.subtype}")
    logging.info(f"audio_codec={audio.audio_codec}")

    audio.download(filename=(f"tempaud.{audio_filetype}"))

    logging.info("Converting temp file using FFMpeg...")

    os.system(FF_PATH + f"ffmpeg -hide_banner -loglevel warning -stats "
              f"-i tempaud.{audio_filetype} -acodec"
              f" libmp3lame \"{vid_title}\".mp3")

    os.system(f"del tempaud.{audio_filetype}")


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
                   help="Downloads all urls specified in textfile in the same"
                   " dir (seperated by new line)")
    parser.add_argument("--quality", "-q", type=str,
                        help="Specifies maximum video resolution e.g. 720p")
    h = parser.add_mutually_exclusive_group()
    h.add_argument("-mkv", action="store_true",
                   help="Specifies output file to be of type mkv")
    h.add_argument("-mp3", action="store_true",
                   help="Specifies output file to be of type mp3")
    args = parser.parse_args()

    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=logging.DEBUG)
    # info,

    download = download_sound if args.mp3 else download_video

    if args.quality and re.fullmatch(r"\d{3,4}p", args.quality):
        args.quality = int(args.quality[:-1])
    else:
        args.quality = 1080

    if args.video:
        if not os.path.exists(DL_PATH):
            os.makedirs(DL_PATH)
        os.chdir(DL_PATH)
        download_iterator(args.video, download)
    elif args.playlist:
        playlist = pytube.Playlist(args.playlist)
        if not os.path.exists(DL_PATH + "/" + convert_title(playlist.title)):
            os.makedirs(DL_PATH + "/" + convert_title(playlist.title))
        download_iterator(list(playlist.video_urls), download)
    elif args.file:
        if (not os.path.exists(DL_PATH + "/"
                               + args.file[:args.file.rfind(".")])):
            os.makedirs(DL_PATH + "/" + args.file[:args.file.rfind(".")])
        with open(args.file, "r") as f:
            links = list(map(str.strip, f.readlines()))
        os.chdir(DL_PATH + "/" + args.file[:args.file.rfind(".")])
        download_iterator(links, download)
    else:
        parser.print_help()
