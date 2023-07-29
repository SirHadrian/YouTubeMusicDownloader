# ==========================
# YouTube Music Downloader #
# ==========================

from time import perf_counter
from argparse import ArgumentParser
from concurrent.futures import wait, ALL_COMPLETED, ThreadPoolExecutor

import yt_dlp


def start(t0):
    def calc(t1):
        return t1-t0
    return calc


# Func to return script run time
stop = start(perf_counter())


# !!! Change the user !!!
USER = 'sirhadrian'

# Change save path if not using Linux.
SAVE_PATH = f'/home/{USER}/Music/YouTubeDownloader'


def refactor_links(links: list) -> list:
    """If the videos are in a playlist or YouTube Mix they need to be
    refactored so that they are pointing to their respective video.

    Args:
        links (list): 'Raw' links

    Returns:
        list: Refactored links
    """

    def refactor_link(link: str) -> str:
        """ If a link contains an '&' it means that it is in a playlist and
        needs to be refactored.
        """
        index = link.find('&')

        return link[:index] if index != -1 else link

    refactored_links = map(refactor_link, links)

    return list(refactored_links)


def download_from_link(link: str, PARAMS: dict) -> None:
    """Downloads multiple YouTube videos and converts them to mp3 using ffmpeg
    according to the FFmpeg params. Also refactors the given links.

    Args:
        PARAMS: YouTubeDl configs; const
        link (list): Link(s) to one or multiple YouTube videos.
    """

    # Videos download and convert with specific params.
    with yt_dlp.YoutubeDL(params=PARAMS) as downloader:
        # Parameter must be a list.
        downloader.download((link,))


def download_from_file(file_name: str) -> list:
    """Downloads and converts all the links from the given file, every link
    must be saved on a new line in the file.

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


def start_thread_workers(
        links: list,
        PARAMS: dict,
        worker_threads: int
) -> None:
    """

    Args:
        links: Workload for the worker threads
        PARAMS: FFmpeg config; const
        worker_threads: number of threads to start
    """
    with ThreadPoolExecutor(worker_threads) as executor:
        def thread_config(target, PARAMS):
            def submit(link):
                return executor.submit(target, link, PARAMS)
            return submit

        future_factory = thread_config(download_from_link, PARAMS)
        futures = map(future_factory, links)

        wait(futures, return_when=ALL_COMPLETED)


def main():
    # Parser object to process the command line options.
    parser = ArgumentParser(
        description='YouTube Music Downloader, Download YouTube contents as \
                mp3 for the given links or txt file'
    )

    # Sub-folder option
    parser.add_argument(
        '-d', '--dir', action='store', type=str, required=False, dest='dir',
        nargs='?', help='Create a subdirectory for the files'
    )
    # Worker Threads option
    parser.add_argument(
        '-t', '--thr', action='store', type=int, required=False, dest='thr',
        nargs='?', help='The number of worker threads(1-16), default 4',
        default=4
    )

    # Download options for the program, can choose only one.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-l', '--links', action='store', nargs='+', metavar='LINK(s)',
        type=str, required=False, dest='links',
        help='The links for the videos to be downloaded'
    )
    group.add_argument(
        '-f', '--file', action='store',
        type=str, required=False, dest='file',
        help='File with the links for the videos to be downloaded'
    )

    # Converting Namespace to dict
    args = vars(parser.parse_args())

    if args['dir'] is not None:
        global SAVE_PATH
        SAVE_PATH = SAVE_PATH + '/' + args['dir']

    worker_threads = args['thr']
    if 1 > worker_threads >= 16:
        worker_threads = 8

    # YouTubeDl params.
    PARAMS = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'outtmpl': SAVE_PATH + '/%(title)s.%(ext)s',
        'default_search': 'ytsearch'
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
    finish = stop(perf_counter())
    print(f'Finished in {round(finish, 2)} second(s)')
