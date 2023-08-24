from concurrent.futures import wait, ALL_COMPLETED, ThreadPoolExecutor

import yt_dlp


def start(t0):
    def calc(t1):
        return t1-t0
    return calc


# !!! Change the user !!!
_USER = 'sirhadrian'

# Change save path if not using Linux.
_SAVE_PATH = f'/home/{_USER}/Music/YouTubeDownloader'

# YouTubeDl params.
_PARAMS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    'outtmpl': _SAVE_PATH + '/%(title)s.%(ext)s',
    'default_search': 'ytsearch'
}


def _refactor_links(links: list) -> list:
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


def _download_from_link(link: str, PARAMS: dict) -> None:
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


def read_file(file_name: str) -> list:
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

    return links


def start_thread_workers(
        links: list,
        worker_threads: int
) -> None:
    """
    Args:
        links: Workload for the worker threads
        PARAMS: FFmpeg config; const
        worker_threads: number of threads to start
    """

    links = _refactor_links(links)

    with ThreadPoolExecutor(worker_threads) as executor:
        def thread_config(target, PARAMS):
            def submit(link):
                return executor.submit(target, link, PARAMS)
            return submit

        future_factory = thread_config(_download_from_link, _PARAMS)
        futures = map(future_factory, links)

        wait(futures, return_when=ALL_COMPLETED)
