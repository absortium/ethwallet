__author__ = 'andrew.shvv@gmail.com'

import hashlib
import os
from random import choice
from string import printable


def random_string(length=30):
    return "".join([choice(printable) for _ in range(length)])


def generate_token():
    return hashlib.sha1(os.urandom(128)).hexdigest()
