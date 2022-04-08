# Youtube snapper

## About

youtube snapper is a lightweight console application build on top of
the pytube module in combination with FFmpeg that allows downloading videos,
playlists and music from youtube in an easy way, without having to handle
downloading and merging streams manually.

## Features

- download youtube videos as mp4, mp3 or mkv in the best available quality by
providing the link
- download a youtube playlist by providing the playlist link

## Use case

while online services of the same kind are fairly common, downloading larger
playlists is either restricted or a premium service for most of the service
providers. This tool has none of such restrictions and is completely free.

## Installation / Setup

- Latest [FFmpeg](https://ffmpeg.org/download.html) executable (*ffmpeg.exe*) downloaded (e.g. from [here](https://github.com/BtbN/FFmpeg-Builds/releases)) and placed in the same  directory
as *youtube_snapper.py*. Alternatively the
relative path may be specified in *youtube_snapper.py*.

- Python Version 3.9.7 or greater

- See *requirments.txt*

## Execution / Usage

Use `python3 youtube_snapper.py` for an overview.

Usage examples for this module:

`python3 youtube_snapper.py -v "VIDEO_URL_1" "VIDEO_URL_2" "VIDEO_URL_3" -q 1440p --mkv`

`python3 youtube_snapper.py -p "PLAYLIST_URL" --mp3`

`python3 youtube_snapper.py -f "PATH_TO_FILE"`

## Additional links

- [pytube module documentation](https://pytube.io/en/latest/api.html#stream-object)

- [FFmpeg documentation](https://ffmpeg.org/ffmpeg.html)
