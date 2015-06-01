# Classic Game Resource Reader (CGRR): Parse resources from classic games.
# Copyright (C) 2015  Tracy Poff
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
import os
import unittest

class Test_kobo_deluxe_a(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import KoboDeluxe
        cls.KoboDeluxe = KoboDeluxe

    def setUp(self):
        self.original_profile = None
        self.test_files_path = os.path.join("test_kobo_deluxe_a")
        self.test_profile_path = os.path.join("test_kobo_deluxe_a", "scores", "Tracy.42")
        with open(self.test_profile_path, "rb") as pfile:
            self.original_profile = pfile.read()

    def test_roundtrip(self):
        """Verify that profile_reader roundtrips data correctly."""
        profile = None
        with open(self.test_profile_path, "rb") as pfile:
            profile_reader = self.KoboDeluxe.get_profile_reader(pfile)
            profile = profile_reader.unpack(pfile.read())
        packed = self.KoboDeluxe.write_profile(profile)

        self.assertEqual(packed, self.original_profile,
            "roundtripped data differs from original")

    def test_export_basic(self):
        """Verify that exporting doesn't die."""
        self.KoboDeluxe.export(self.test_files_path)
