#!/usr/bin/python

import distutils.core as mod_distutilscore

mod_distutilscore.setup( name = 'gpxpy',
	version = '0.5',
	description = 'GPX file parser and GPS track manipulation library',
	license = 'GPL',
	author = 'Tomo Krajina',
	author_email = 'tkrajina@gmail.com',
	url = 'http://www.trackprofiler.com/gpxpy/index.html',
	packages = [
		'gpxpy',
	],
)
