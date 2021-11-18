#!./.ve/bin/python3


# ==========================
# YouTube Music Downloader
# ==========================


import youtube_dl


TEST_LINK = 'https://www.youtube.com/watch?v=2YTBgFmK_bs'
TEST_LINK_MIX = 'https://www.youtube.com/watch?v=2YTBgFmK_bs&list=RD2YTBgFmK_bs&start_radio=1&rv=2YTBgFmK_bs&t=0'


# !!! Change the user !!!
USER = 'sirhadrian'

# Change save path if not using Linux.
SAVE_PATH = f'/home/{USER}/Music/YouTubeDownloader'

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


def refactorLinks(links: list) -> list:
    """If the videos are in a playlist or YouTube Mix they need to be refactored so
    that they are pointing to their respective video.

    Args:
        links (list): 'Raw' links

    Returns:
        list: Refactored links
    """

    refactored_links = []

    for link in links:
        # If a link contains an '&' it meens that it is in a playlist and needs to
        # be refactored.
        index = link.find('&')

        if index != -1:
            refactored_links.append(link[:index])
        else:
            refactored_links.append(link)

    return refactored_links


def downloadFromLinks(links: list) -> None:
    """Downloads multiple youtube videos and converts them to mp3 using ffmpeg 
    according with the FFmpeg params. Also refactors the given links.

    Args:
        links (lsit): Link(s) to one or multiple youtube videos.
    """

    # Videos download and convert with specific params.
    with youtube_dl.YoutubeDL(params=PARAMS) as downloader:
        # Parameter must be a list.
        downloader.download(refactorLinks(links))


def downloadFromFile(fileName: str) -> None:
    """Downloads and converts all the links from the given file, every link must be saved 
    on a new line in the file.

    Args:
        fileName (str): The file handler.
    """

    # Geting all the raw links from the file.
    with open(fileName, 'r') as file:
        links = file.readlines()

    # Stripping all the unwanted '\n' from the links.
    links = [link.strip('\n') for link in links]

    # Links are refactored inside the function.
    downloadFromLinks(links)


def main():
    pass


if __name__ == "__main__":
    downloadFromLinks(TEST_LINK_MIX)
