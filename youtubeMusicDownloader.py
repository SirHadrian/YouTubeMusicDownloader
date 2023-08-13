# ==========================
# YouTube Music Downloader #
# ==========================

from time import perf_counter
from argparse import ArgumentParser

from downloader import Downloader, start


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

    save_path = ''
    if args['dir'] is not None:
        save_path += '/' + args['dir']

    # Downloader instance
    downloader = Downloader('sirhadrian', save_path)

    worker_threads = args['thr']
    if 1 > worker_threads >= 16:
        worker_threads = 8

    if args['links'] is not None:
        print('---STARTED DOWNLOADING FROM THE LINK(s)---')
        downloader.start_thread_workers(args['links'],  worker_threads)

    elif args['file'] is not None:
        print('---STARTED DOWNLOADING FORM THE FILE---')
        links = downloader.read_file(args['file'])
        downloader.start_thread_workers(links,  worker_threads)


if __name__ == "__main__":
    stop = start(perf_counter())
    main()
    finish = stop(perf_counter())
    print(f'Finished in {round(finish, 2)} second(s)')
