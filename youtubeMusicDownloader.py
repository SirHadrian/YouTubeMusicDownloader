#!./.ve/bin/python3


import youtube_dl

TEST_LINK = 'https://www.youtube.com/watch?v=2YTBgFmK_bs'
TEST_LINK_MIX = 'https://www.youtube.com/watch?v=2YTBgFmK_bs&list=RD2YTBgFmK_bs&start_radio=1&rv=2YTBgFmK_bs&t=0'


# Change the user
USER = 'sirhadrian'
# Change save path if not using Linux
SAVE_PATH = f'/home/{USER}/Music/YouTubeDownloader'
# FFmpeg params
params = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    'outtmpl': SAVE_PATH + '/%(title)s.%(ext)s'
}


def downloadFromLink(link: str) -> None:
    """Downloads a single youtube video and converts it using ffmpeg according with the FFmpeg params

    Args:
        link (str): Link to the a single video
    """

    # If the video is in a playlist or YouTube Mix the link needs to be refactored
    # so that it's pointing to the individual video
    index = link.find('&')
    
    if index != -1:
        link = link[:index]
    
    # Video downloading and converting
    with youtube_dl.YoutubeDL(params=params) as downloader:
        # Parameter must be a list
        downloader.download([link])


def main():
    pass


if __name__ == "__main__":
    downloadFromLink(TEST_LINK_MIX)
