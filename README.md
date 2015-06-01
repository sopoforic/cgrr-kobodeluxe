kobodeluxe
==========

This module reads and writes score and profile files for Kobo Deluxe, a game by
David Olofson.

Usage
=====

Use `read_profiles` to get a list of parsed profiles:

```python
>>> kobodeluxe.read_profiles("path/to/kobo")
[{
    'start_chunk':
    {
        'best_score': 39559,
        'last_scene': 22,
        'name': 'Tracy'
    },
    'prof_chunk':
    {
        'handicap': 0,
        'color2': -1,
        'profile_chunk_header': b'PROF',
        'profile_chunk_length': 20,
        'version': 1,
        'skill': 1,
        'color1': -1
    },
    'score_chunk':
    [{
        'start_scene': 0,
        'hiscore_chunk_length': 48,
        'skill': 0,
        'score': 2581,
        'end_lives': 5,
        'end_health': 1,
        'hiscore_chunk_header': b'HISC',
        'playtime': 3580,
        'start_date': 0,
        'gametype': 0,
        'loads': 0,
        'end_date': 0,
        'end_scene': 2,
        'saves': 0
    }]
}]
```

Use `export` to generate an HTML report of the profiles and scores:

```python
with open("report.html", "wb") as report_file:
    report_file.write(kobodeluxe.export("path/to/kobo"))
```

Use `write_profile` to export a modified profile back to disk:

```python
profiles = kobodeluxe.read_profiles("path/to/kobo")
profile = profiles[0] # pick one
# modify the profile dictionary as desired
with open("path/to/profile", "wb") as pfile:
    pfile.write(kobodeluxe.write_profile(profile))
```

Requirements
============

* Python 2.7+ or 3.3+
    * No python 2.6 or 3.2.
* cgrr from https://github.com/sopoforic/cgrr
* jinja2 (if you want to do an html export)

You can install these dependencies with `pip install -r requirements.txt`.

License
=======

This module is available under the GPL v3 or later. See the file COPYING for
details.

[![Build Status](https://travis-ci.org/sopoforic/cgrr-kobodeluxe.svg?branch=master)](https://travis-ci.org/sopoforic/cgrr-kobodeluxe)
[![Code Health](https://landscape.io/github/sopoforic/cgrr-kobodeluxe/master/landscape.svg?style=flat)](https://landscape.io/github/sopoforic/cgrr-kobodeluxe/master)
