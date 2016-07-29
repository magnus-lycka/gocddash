#!/usr/bin/env python3

import argparse


def main():
    """ Runs program and handles CLI interaction """

    parser = argparse.ArgumentParser(
        description='''\
Download pipeline data from GO.CD and store locally.
Sample usage: go_cli pull -p pipeline-name
              go_cli pull -p pipeline-name -s 1900 -n 10
              go_cli pull -p pipeline-name -s 750''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'action',
        choices=['pull', 'info', 'export'])
    parser.add_argument(
        '-p', '--pipeline', type=str, default=None, help="Which PIPELINE to use.")
    parser.add_argument(
        '-d', '--dry-run', action='store_true', default=False, help="Dry-run a command, without syncronizing or saving any data.")
    parser.add_argument(
        '-n', '--next', type=int, default=None,
        help="Pull the subsequent NEXT number of pipeline counts from GO. Defaults to the number of pipelines currently not synced locally.")
    parser.add_argument(
        '-s', '--start', type=int, default=0, help="Pull from START pipeline count.")
    parser.add_argument(
        '-f', '--filename', type=str, default="cli_save", help="FILENAME to save in ~/GO_CSV/"
    )

    pargs = parser.parse_args()

    from gocddash.analysis import go_request
    from gocddash.analysis import actions

    if pargs.action == 'pull':
        if not pargs.pipeline:
            raise ValueError("No pipeline specified.")
        if pargs.next is None:
            pargs.next = go_request.get_max_pipeline_status(pargs.pipeline)[0] - pargs.start
        actions.pull(pargs.pipeline, pargs.next, pargs.start, pargs.dry_run)
    elif pargs.action == 'export':
        if not pargs.pipeline:
            raise ValueError("No pipeline specified.")
        actions.export(pargs.pipeline, "~/GO_CSV/" + pargs.filename + ".csv", pargs.dry_run)
    elif pargs.action == 'info':
        if (pargs.pipeline):
            actions.info(pargs.pipeline)
        else:
            actions.all_info()
    else:
        print ("I have nothing to do.")

if __name__ == '__main__':
    main()
