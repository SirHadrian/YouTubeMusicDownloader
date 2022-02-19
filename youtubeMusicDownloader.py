#!venv/bin/python3

# ==========================
# YouTube Music Downloader #
# ==========================

import youtube_dl
import time
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

start = time.perf_counter()

# !!! Change the user !!!
USER = 'sirhadrian'

# Change save path if not using Linux.
SAVE_PATH = f'/home/{USER}/Music/YouTubeDownloader'


def refactor_links(links: list) -> list:
    """If the videos are in a playlist or YouTube Mix they need to be refactored so
    that they are pointing to their respective video.

    Args:
        links (list): 'Raw' links

    Returns:
        list: Refactored links
    """

    refactored_links = []

    for link in links:
        # If a link contains an '&' it means that it is in a playlist and needs to be refactored.
        index = link.find('&')

        if index != -1:
            refactored_links.append(link[:index])
        else:
            refactored_links.append(link)

    return refactored_links


def download_from_link(link: str, params: dict) -> None:
    """Downloads multiple YouTube videos and converts them to mp3 using ffmpeg
    according to the FFmpeg params. Also refactors the given links.

    Args:
        params: YouTubeDl configs
        link (list): Link(s) to one or multiple YouTube videos.
    """

    # Videos download and convert with specific params.
    with youtube_dl.YoutubeDL(params=params) as downloader:
        # Parameter must be a list.
        downloader.download((link,))


def download_from_file(file_name: str) -> list:
    """Downloads and converts all the links from the given file, every link must be saved 
    on a new line in the file.

    Args:
        file_name (str): The file handler.

    Returns:
        list: Refactored links
    """

    # Getting all the raw links from the file.
    with open(file_name, 'r') as file:
        links = file.readlines()

    # Stripping all the unwanted '\n' from the links.
    links = [link.strip('\n') for link in links]

    return refactor_links(links)


def start_thread_workers(links: list, params: dict, worker_threads: int) -> None:
    """

    Args:
        links: Workload for the worker threads
        params: FFmpeg config
        worker_threads: number of threads to start

    Returns:

    """
    thread_pool = ThreadPoolExecutor(worker_threads)
    futures = []
    for link in links:
        futures.append(thread_pool.submit(download_from_link, link, params))
    wait(futures, return_when=ALL_COMPLETED)


def main():
    # Parser object to process the command line options.
    parser = ArgumentParser(description='YouTube Music Downloader, Download YouTube contents as mp3 for the '
                                        'given links or txt file')

    # Sub-folder option
    parser.add_argument('-d', '--dir', action='store', type=str, required=False, dest='dir',
                        nargs='?', help='Create a subdirectory for the files')
    # Worker Threads option
    parser.add_argument('-n', '--thr', action='store', type=int, required=False, dest='thr',
                        nargs='?', help='The number of worker threads(1-16), default 4', default=4)

    # Download options for the program, can choose only one.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--links', action='store', nargs='+', metavar='LINK(s)',
                       type=str, required=False, dest='links',
                       help='The links for the videos to be downloaded')
    group.add_argument('-f', '--file', action='store',
                       type=str, required=False, dest='file',
                       help='File with the links for the videos to be downloaded')

    # Converting Namespace to dict
    args = vars(parser.parse_args())

    if args['dir'] is not None:
        global SAVE_PATH
        SAVE_PATH = SAVE_PATH + '/' + args['dir']

    worker_threads = args['thr']
    if 1 > worker_threads >= 16:
        worker_threads = 4

    # FFmpeg params.
    PARAMS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'outtmpl': SAVE_PATH + '/%(title)s.%(ext)s'
    }

    if args['links'] is not None:
        print('---STARTED DOWNLOADING FROM THE LINK(s)---')
        links = refactor_links(args['links'])
        start_thread_workers(links, PARAMS, worker_threads)

    elif args['file'] is not None:
        print('---STARTED DOWNLOADING FORM THE FILE---')
        links = download_from_file(args['file'])
        start_thread_workers(links, PARAMS, worker_threads)


if __name__ == "__main__":
    main()
    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s)')
