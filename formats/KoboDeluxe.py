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

import yapsy
from jinja2 import Environment, FileSystemLoader

import utilities
from utilities import File, FileReader

env = Environment(loader=FileSystemLoader('./formats'))

class KoboDeluxe(yapsy.IPlugin.IPlugin):
    """Parses KoboDeluxe data."""

    key = "kobo_deluxe_a"
    title = "Kobo Deluxe"
    developer = "David Olofson"
    description = "Kobo Deluxe v0.5.1"

    identifying_files = [
        File("kobodl.exe", 510976,  "c0f6b8ad7563bd0d9e54872778c69104"),
    ]

    @staticmethod
    def read_all_scores(scoredata):
        """Return a list of decoded scores from the hiscore chunk scoredata."""
        n = KoboDeluxe.hiscore_reader.struct.size
        scores = [scoredata[i:i+n] for i in range(0, len(scoredata), n)]
        return list(map(KoboDeluxe.hiscore_reader.unpack, scores))

    @staticmethod
    def write_all_scores(scores):
        return b''.join(map(KoboDeluxe.hiscore_reader.pack, scores))

    @staticmethod
    def get_profile_reader(profile_file=None, profile_data=None):
        if not (profile_file or profile_data) or (profile_file and profile_data):
            raise ValueError("Must provide exactly one of profile_file or profile_data.")
        if profile_file:
            score_size = (os.fstat(profile_file.fileno()).st_size
                                   - KoboDeluxe.start_reader.struct.size
                                   - KoboDeluxe.prof_reader.struct.size)
        else:
            score_size = KoboDeluxe.hiscore_reader.struct.size * len(profile_data['score_chunk'])
        return FileReader(
            format = [
                ("start_chunk", "{}s".format(KoboDeluxe.start_reader.struct.size)),
                ("prof_chunk", "{}s".format(KoboDeluxe.prof_reader.struct.size)),
                ("score_chunk", "{}s".format(score_size)),
            ],
            massage_in = {
                "start_chunk" : (KoboDeluxe.start_reader.unpack),
                "prof_chunk" : (KoboDeluxe.prof_reader.unpack),
                "score_chunk" : (KoboDeluxe.read_all_scores),
            },
            massage_out = {
                "start_chunk" : (KoboDeluxe.start_reader.pack),
                "prof_chunk" : (KoboDeluxe.prof_reader.pack),
                "score_chunk" : (KoboDeluxe.write_all_scores),
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

    @staticmethod
    def export(path, format="html"):
        """Export a report of  everything this class supports."""
        global env
        if format == "html":
            template = env.get_template('KoboDeluxe.html')
        profiles = KoboDeluxe.read_profiles(path)
        text = template.render({
            "key" : KoboDeluxe.key,
            "title" : KoboDeluxe.title,
            "developer" : KoboDeluxe.developer,
            "description" : KoboDeluxe.description,
            "profiles" : profiles,
            })
        return text

    @staticmethod
    def verify(path):
        """Verifies that the provided path is the supported game."""
        return utilities.verify(KoboDeluxe.identifying_files, path)

    @staticmethod
    def read_profiles(path):
        """Reads all profiles found in path."""
        profiles = [os.path.join(path, "scores", pfile) for pfile in os.listdir(os.path.join(path, "scores"))]
        answer = []
        for pfile in profiles:
            with open(pfile, "rb") as profile:
                profile_reader = KoboDeluxe.get_profile_reader(profile)
                answer.append(profile_reader.unpack(profile.read()))
        return answer

    @staticmethod
    def write_profile(profile):
        """Return a bytestring representation of profile."""
        profile_reader = KoboDeluxe.get_profile_reader(profile_data=profile)
        return profile_reader.pack(profile)
