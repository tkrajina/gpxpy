#!/usr/bin/env python

"""
Command line utility to extract basic statistics from gpx file(s)
"""

import pdb

import sys as mod_sys
import logging as mod_logging
import math as mod_math
import argparse as mod_argparse

import gpxpy as mod_gpxpy
import gpxpy.gpx as mod_gpx

from typing import *

KM_TO_MILES = 0.621371
M_TO_FEET = 3.28084


def format_time(time_s: float) -> str:
    if not time_s:
        return 'n/a'
    elif args.seconds:
        return str(int(time_s))
    else:
        mins, secs = divmod(int(time_s), 60)
        hrs, mins = divmod(mins, 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"


def format_long_length(length: float) -> str:
    if args.miles:
        return f'{length / 1000. * KM_TO_MILES:.3f}miles'
    else:
        return f'{length / 1000.:.3f}km'


def format_short_length(length: float) -> str:
    if args.miles:
        return f'{length * M_TO_FEET:.2f}ft'
    else:
        return f'{length:.2f}m'


def format_speed(speed: float) -> str:
    if not speed:
        speed = 0
    if args.miles:
        return f'{speed * KM_TO_MILES * 3600. / 1000.:.2f}mph'
    else:
        return f'{speed:.2f}m/s = {speed * 3600. / 1000.:.2f}km/h'


def print_gpx_part_info(gpx_part: Union[mod_gpx.GPX, mod_gpx.GPXTrack, mod_gpx.GPXTrackSegment], indentation: str='    ') -> None:
    """
    gpx_part may be a track or segment.
    """
    length_2d = gpx_part.length_2d()
    length_3d = gpx_part.length_3d()
    print(f'{indentation}Length 2D: {format_long_length(length_2d or 0)}')
    print(f'{indentation}Length 3D: {format_long_length(length_3d)}')

    moving_data = gpx_part.get_moving_data()
    raw_moving_data = gpx_part.get_moving_data(raw=True)
    if moving_data:
        print(f'{indentation}Moving time: {format_time(moving_data.moving_time)}')
        print(f'{indentation}Stopped time: {format_time(moving_data.stopped_time)}')
        print(f'{indentation}Max speed: {format_speed(moving_data.max_speed)} (raw: {format_speed(raw_moving_data.max_speed) if raw_moving_data else "?"})')
        print(f'{indentation}Avg speed: {format_speed(moving_data.moving_distance / moving_data.moving_time) if moving_data.moving_time > 0 else "?"}')

    uphill, downhill = gpx_part.get_uphill_downhill()
    print(f'{indentation}Total uphill: {format_short_length(uphill)}')
    print(f'{indentation}Total downhill: {format_short_length(downhill)}')

    start_time, end_time = gpx_part.get_time_bounds()
    print(f'{indentation}Started: {start_time}')
    print(f'{indentation}Ended: {end_time}')

    points_no = len(list(gpx_part.walk(only_points=True)))
    print(f'{indentation}Points: {points_no}')

    if points_no > 0:
        distances: List[float] = []
        previous_point = None
        for point in gpx_part.walk(only_points=True):
            if previous_point:
                distance = point.distance_2d(previous_point)
                distances.append(distance)
            previous_point = point
        print(f'{indentation}Avg distance between points: {format_short_length(sum(distances) / len(list(gpx_part.walk())))}')

    print('')


def print_gpx_info(gpx: mod_gpx.GPX, gpx_file: str) -> None:
    print(f'File: {gpx_file}')

    if gpx.name:
        print(f'  GPX name: {gpx.name}')
    if gpx.description:
        print(f'  GPX description: {gpx.description}')
    if gpx.author_name:
        print(f'  Author: {gpx.author_name}')
    if gpx.author_email:
        print(f'  Email: {gpx.author_email}')

    print_gpx_part_info(gpx)

    for track_no, track in enumerate(gpx.tracks):
        for segment_no, segment in enumerate(track.segments):
            print(f'    Track #{track_no}, Segment #{segment_no}')
            print_gpx_part_info(segment, indentation='        ')


def run(gpx_files: List[str]) -> None:
    if not gpx_files:
        print('No GPX files given')
        mod_sys.exit(1)

    for gpx_file in gpx_files:
        try:
            gpx = mod_gpxpy.parse(open(gpx_file))
            print_gpx_info(gpx, gpx_file)
        except Exception as e:
            mod_logging.exception(e)
            print(f'Error processing {gpx_file}')
            mod_sys.exit(1)


def make_parser() -> mod_argparse.ArgumentParser:
    parser = mod_argparse.ArgumentParser(usage='%(prog)s [-s] [-m] [-d] [file ...]',
        description='Command line utility to extract basic statistics from gpx file(s)')
    parser.add_argument('-s', '--seconds', action='store_true',
                        help='print times as N seconds, rather than HH:MM:SS')
    parser.add_argument('-m', '--miles', action='store_true',
                        help='print distances and speeds using miles and feet')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='show detailed logging')
    return parser

if __name__ == '__main__':
    args, gpx_files = make_parser().parse_known_args()
    if args.debug:
        mod_logging.basicConfig(level=mod_logging.DEBUG,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    run(gpx_files)
