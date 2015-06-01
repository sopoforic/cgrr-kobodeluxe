# Classic Game Resource Reader (CGRR): Parse resources from classic games.
# Copyright (C) 2014  Tracy Poff
#
# This file is part of CGRR.
#
# CGRR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CGRR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CGRR.  If not, see <http://www.gnu.org/licenses/>.
"""Parses Kobo Deluxe data."""
import logging
import os

import cgrr
from cgrr import File, FileReader

key = "kobo_deluxe_a"
title = "Kobo Deluxe"
developer = "David Olofson"
description = "Kobo Deluxe v0.5.1"

identifying_files = [
    File("kobodl.exe", 510976,  "c0f6b8ad7563bd0d9e54872778c69104"),
]

def read_all_scores(scoredata):
    """Return a list of decoded scores from the hiscore chunk scoredata."""
    n = hiscore_reader.struct.size
    scores = [scoredata[i:i+n] for i in range(0, len(scoredata), n)]
    return list(map(hiscore_reader.unpack, scores))

def write_all_scores(scores):
    return b''.join(map(hiscore_reader.pack, scores))

def get_profile_reader(profile_file=None, profile_data=None):
    """Return a FileReader suited to the profile passed in.

    If profle_file is passed, it should be an open profile file. If
    profile_data is passed, it should be an unpacked profile.

    """
    if not (profile_file or profile_data) or (profile_file and profile_data):
        raise ValueError("Must provide exactly one of profile_file or profile_data.")
    if profile_file:
        score_size = (os.fstat(profile_file.fileno()).st_size
                               - start_reader.struct.size
                               - prof_reader.struct.size)
    else:
        score_size = hiscore_reader.struct.size * len(profile_data['score_chunk'])
    return FileReader(
        format = [
            ("start_chunk", "{}s".format(start_reader.struct.size)),
            ("prof_chunk", "{}s".format(prof_reader.struct.size)),
            ("score_chunk", "{}s".format(score_size)),
        ],
        massage_in = {
            "start_chunk" : (start_reader.unpack),
            "prof_chunk" : (prof_reader.unpack),
            "score_chunk" : (read_all_scores),
        },
        massage_out = {
            "start_chunk" : (start_reader.pack),
            "prof_chunk" : (prof_reader.pack),
            "score_chunk" : (write_all_scores),
        },
        byte_order = "<"
    )

start_reader = FileReader(
    format = [
        ("best_score", "I"),
        ("last_scene", "i"),
        ("name", "64s"),
    ],
    massage_in = {
        "name" : (lambda s: s.decode('ascii').strip('\x00'))
    },
    massage_out = {
        "name" : (lambda s: s.encode('ascii'))
    },
    byte_order = "<"
)

prof_reader = FileReader(
    format = [
        ("profile_chunk_header", "4s"), # PROF
        ("profile_chunk_length", "I"),  # 20 (14h)
        ("version", "I"),
        ("skill", "i"),
        ("handicap", "i"),              # 0 == none
        ("color1", "i"),                # -1 == default
        ("color2", "i"),                # -1 == default
    ],
    byte_order="<"
)

# For values below, -1 (signed) or 0 (unsigned) mean "unknown"
hiscore_reader = FileReader(
    format = [
        ("hiscore_chunk_header", "4s"), # HISC
        ("hiscore_chunk_length", "I"),  # 48 (30h)
        ("start_date", "I"),
        ("end_date", "I"),
        ("skill", "i"),
        ("score", "I"),
        ("start_scene", "i"),
        ("end_scene", "i"),
        ("end_lives", "i"),
        ("end_health", "i"),
        ("playtime", "I"),
        ("saves", "i"),
        ("loads", "i"),
        ("gametype", "i"),
    ],
    byte_order="<"
)

def export(path, format="html"):
    """Export a report of  everything this class supports."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader('.'))

    if format == "html":
        template = env.get_template('kobodeluxe.html')
    profiles = read_profiles(path)
    text = template.render({
        "key" : key,
        "title" : title,
        "developer" : developer,
        "description" : description,
        "profiles" : profiles,
        })
    return text

def verify(path):
    """Verifies that the provided path is the supported game."""
    return cgrr.verify(identifying_files, path)

def read_profiles(path):
    """Reads all profiles found in path."""
    profiles = [os.path.join(path, "scores", pfile) for pfile in os.listdir(os.path.join(path, "scores"))]
    answer = []
    for pfile in profiles:
        with open(pfile, "rb") as profile:
            profile_reader = get_profile_reader(profile)
            answer.append(profile_reader.unpack(profile.read()))
    return answer

def write_profile(profile):
    """Return a bytestring representation of profile."""
    profile_reader = get_profile_reader(profile_data=profile)
    return profile_reader.pack(profile)
