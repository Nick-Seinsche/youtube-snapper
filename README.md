# youtube downloader

youtube downloader is a lightweight console application build on top of
the pytube module in combination with FFmpeg that allows downloading videos,
playlists and music from youtube in an easy way, without having to handle
downloading and merging streams manually.

## features

- download youtube videos as mp4, mp3 or mkv in the best available quality by
providing the link
- download a youtube playlist by providing the playlist link

## use case

while online services of the same kind are fairly common, downloading larger
playlists is either restricted or a premium service for most of the service
providers. This tool has none of such restrictions and is completely free.

## installation / setup

- Latest [FFmpeg](https://ffmpeg.org/download.html) executable downloaded and
placed in the same directory as *youtube_downloader.py*. Alternatively the
relative path may be specified in *youtube_downloader.py*.

- See *requirments.txt*

## execution / usage

Use `python3 youtube_downloader.py` for an overview.

Usage examples for this module:

`python3 youtube_downloader.py -v "VIDEO_URL_1" "VIDEO_URL_2" "VIDEO_URL_3" --hq --mkv`

`python3 youtube_downloader.py -p "PLAYLIST_URL" --mp3`

`python3 youtube_downloader.py -f "PATH_TO_FILE"`

## additional links

- [pytube module documentation](https://pytube.io/en/latest/api.html#stream-object)

- [FFmpeg documentation](https://ffmpeg.org/ffmpeg.html)
