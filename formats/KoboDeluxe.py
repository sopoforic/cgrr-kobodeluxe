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
    
    start_reader = FileReader([
        ("best_score", "I"),
        ("last_scene", "i"),
        ("name", "64s"),
        ], byte_order="<")

    prof_reader = FileReader([
        ("profile_chunk_header", "4s"), # PROF
        ("profile_chunk_length", "I"),  # 20 (14h)
        ("version", "I"),
        ("skill", "i"),
        ("handicap", "i"),              # 0 == none
        ("color1", "i"),                # -1 == default
        ("color2", "i"),                # -1 == default
        ], byte_order="<")

    # For values below, -1 (signed) or 0 (unsigned) mean "unknown"
    hiscore_reader = FileReader([
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
        ], byte_order="<")

    @staticmethod
    def export(path, format="html"):
        """Exports everything this class supports."""
        # fixme: can't verify in here
        # if not cls.verify(path):
        #     raise Exception
        global env
        if format == "html":
            template = env.get_template('KoboDeluxe.html')
        profiles = KoboDeluxe.read_profile(path)
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
    def read_profile(path):
        """Reads profile found in path."""
        profiles = [os.path.join(path, "scores", pfile) for pfile in os.listdir(os.path.join(path, "scores"))]
        answer = []
        for pfile in profiles:
            with open(pfile, "rb") as profile:
                data = profile.read(KoboDeluxe.start_reader.struct.size)
                start = KoboDeluxe.start_reader.unpack(data)
                data = profile.read(KoboDeluxe.prof_reader.struct.size)
                prof = KoboDeluxe.prof_reader.unpack(data)
                scores = []
                for data in iter(lambda: profile.read(KoboDeluxe.hiscore_reader.struct.size), b""):
                    scores.append(KoboDeluxe.hiscore_reader.unpack(data))
                answer.append((start, prof, scores))
        return answer
