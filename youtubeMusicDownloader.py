#!./.ve/bin/python3


# ==========================
# YouTube Music Downloader
# ==========================


from argparse import ArgumentParser
import youtube_dl


# !!! Change the user !!!
USER = 'sirhadrian'

# Change save path if not using Linux.
SAVE_PATH = f'/home/{USER}/Music/YouTubeDownloader'



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


def downloadFromLinks(links: list, PARAMS: dict) -> None:
    """Downloads multiple youtube videos and converts them to mp3 using ffmpeg 
    according with the FFmpeg params. Also refactors the given links.

    Args:
        links (lsit): Link(s) to one or multiple youtube videos.
    """

    # Videos download and convert with specific params.
    with youtube_dl.YoutubeDL(params=PARAMS) as downloader:
        # Parameter must be a list.
        downloader.download(refactorLinks(links))


def downloadFromFile(fileName: str, PARAMS: dict) -> None:
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
    downloadFromLinks(links, PARAMS)


def main():
    # Parser object to process the command line options.
    parser = ArgumentParser(description="YouTube Music Downloader",
                            add_help='Download YouTube contents as mp3 for the given links or txt file')

    # Subfolder option
    parser.add_argument('-d', '--dir', action='store', type=str, required=False, dest='dir',
                        nargs='?', help='Create a subdirectory for the files')

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

    if args['dir'] != None:
        global SAVE_PATH
        SAVE_PATH = SAVE_PATH + '/' + args['dir']

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

    if args['links'] != None:
        print('---STARTED DOWNLOADING FROM THE LINK(s)---')
        downloadFromLinks(args['links'], PARAMS)

    elif args['file'] != None:
        print('---STARTED DOWNLOADING FORM THE FILE---')
        downloadFromFile(args['file'], PARAMS)


if __name__ == "__main__":
    main()
