#!/usr/bin/env python3
from alive_progress import alive_bar
import os
import pytube
from pytube import Playlist
from colorama import Fore
import shutil
import concurrent.futures

PLAYLIST_LINK = "https://www.youtube.com/watch?v=9o8wGVAAReo&list=PLjzSBgd8kSOUg3aad1nBc4IhHJLqBQM_6&ab_channel=SSSniperWolf"
VIDEO_FOLDER = "videos/"
MAX_THREADS = 8
USE_PARALLEL = True
# check that computer has enough space to download all videos
CHECK_ENOUGH_SPACE = False

def clearFolder():
    print("clearing videos folder...")
    file_list = os.listdir(VIDEO_FOLDER)
    with alive_bar(len(file_list)) as bar:
        for filename in file_list:
            file_path = os.path.join(VIDEO_FOLDER, filename)
            try:
                os.remove(file_path)
                print(f"{Fore.GREEN}V{Fore.RESET} deleted {Fore.YELLOW}{file_path}{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}X{Fore.RESET}Failed to delete {Fore.YELLOW}{file_path}{Fore.RESET}. Reason: {e}")
            bar()



def estimate_video_size(video: pytube.YouTube):
    try:
        stream = video.streams.get_highest_resolution()
        return stream.filesize
    except pytube.exceptions.AgeRestrictedError:
        print(f"video {video.watch_url} is age restricted :(")
        return 0

def estimateUsage(playlist : Playlist) -> bool:
    # disk information:
    video_sizes = 0.0
    total, used, free = shutil.disk_usage("/")    

    with alive_bar(len(playlist.video_urls)) as bar:
        for video in playlist.videos:
            size = estimate_video_size(video)
            video_sizes += size
            bar()    
    
    # /1e9 is byte to gb
    print(f"{Fore.YELLOW} total space on computer: {total/1e9:.2f} GB{Fore.RESET}")
    print(f"{Fore.YELLOW} total used space on computer: {used/1e9:.2f} GB{Fore.RESET}")
    print(f"{Fore.YELLOW} total free space on computer: {free/1e9:.2f} GB{Fore.RESET}")
    print(f"{Fore.YELLOW} total videos size: {video_sizes/1e9:.2f} GB{Fore.RESET}")

    return free - video_sizes > 0


def downloadPlaylist(playlist: Playlist):
    print("downloading videos...")
    with alive_bar(len(playlist.videos)) as bar:
        def downloadVideo(video_obj: tuple[int, pytube.YouTube]) -> None:
            try:
                num_of_video, video = video_obj 
                stream = video.streams.get_highest_resolution()
                
                if stream is None:
                    raise Exception("Stream not found.")
                
                file_location = stream.download(VIDEO_FOLDER, filename_prefix=num_of_video)
                if (os.path.exists(file_location)):
                    print(f"{Fore.GREEN}V{Fore.RESET} downloaded {Fore.LIGHTYELLOW_EX}{video.title}{Fore.RESET} file path {Fore.LIGHTYELLOW_EX}{file_location}{Fore.RESET} size {Fore.GREEN}{os.path.getsize(file_location)/1e9:.4f} GB{Fore.RESET}")
                else:
                    raise Exception(f"could not download video {video.watch_url}. file stream: {stream}")
            except Exception as e:
                print(f"{Fore.RED}X{Fore.RESET}Failed to download {Fore.LIGHTYELLOW_EX}{video.title}{Fore.RESET}. Reason: {e}")
            bar()
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS if USE_PARALLEL else 1) as executor:
             executor.map(downloadVideo, enumerate(playlist.videos))

def main():
    clearFolder()
    playlist = Playlist(PLAYLIST_LINK)
    print("estimating usage....")
    
    # skip this if you know you have enough storage
    if CHECK_ENOUGH_SPACE and not estimateUsage(playlist):
        print("not enough space on computer")
        return

    downloadPlaylist(playlist)
    
            




if __name__ == "__main__":
    main()