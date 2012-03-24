#!/usr/bin/env python

from distutils.core import setup, Extension

setup(	name="spi",
	version="1.6",
	description="Python SPI access through C module for the BeagleBone",
	author="Branden Hall",
	author_email="bhall@automatastudios.com",
	maintainer="none",
	maintainer_email="none",
	license="GPLv2",
	url="http://www.waxpraxis.org",
	ext_modules=[Extension("spi", ["spimodule.c"])])


