from concurrent.futures import wait, ALL_COMPLETED, ThreadPoolExecutor


import yt_dlp


def start(t0):
    def calc(t1):
        return t1-t0
    return calc


class Downloader():
    def __init__(self, user_name, save_path):
        self._user_name = 'sirhadrian'
        self._save_path = f'/home/{self._user_name}/Music/YouTubeDownloader' \
            + save_path
        # YouTubeDl params.
        self._PARAMS = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'outtmpl': self._save_path + '/%(title)s.%(ext)s',
            'default_search': 'ytsearch'
        }

    def _prepare_links(links: list) -> list:
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

    def download_from_link(self, link: str) -> None:
        """Downloads YouTube videos and converts them to mp3 using ffmpeg
        according to the FFmpeg params. Also refactors the given links.

        Args:
            PARAMS: YouTubeDl configs; const
            link (list): Link(s) to one or multiple YouTube videos.
        """

        link = self._prepare_links(list(link))

        # Videos download and convert with specific params.
        with yt_dlp.YoutubeDL(params=self._PARAMS) as downloader:
            # Parameter must be a list.
            downloader.download(link)

    def read_file(self, file_name: str) -> list:
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

        return self._prepare_links(links)

    def start_thread_workers(
            self,
            links: list,
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

            future_factory = thread_config(
                self.download_from_link, self._PARAMS)

            futures = map(future_factory, links)
            wait(futures, return_when=ALL_COMPLETED)
