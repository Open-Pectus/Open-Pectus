""" Pectus is a process control system for Unit Operations such as filtration, chromatography, precipitation,
solubilization and refolding. Pectus implements a language called P-code which is used to write methods and
control components on the Unit Operation. """
__version__ = "0.0.1"

import logging

import colorlog


def log_setup_colorlog(root_loglevel: int = logging.INFO):
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:%(message)s'))

    logging.root.setLevel(root_loglevel)
    logging.root.handlers.clear()
    logging.root.addHandler(handler)
