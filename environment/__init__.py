"""
References:

https://wellfire.co/blog/easier-12-factor-django/
"""
import os
import re


def read_env():
    """Pulled from Honcho code with minor updates, reads local default
    environment variables from a .env file located in the project root
    directory.
    """
    try:
        with open(".env") as f:
            content = f.read()
    except IOError:
        content = ""

    for line in content.splitlines():
        m1 = re.match(r"\A([A-Za-z_0-9]+)=(.*)\Z", line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)
            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r"\\(.)", r"\1", m3.group(1))
            os.environ.setdefault(key, val)


def env_var(key, default=None):
    """Retrieves env vars and makes Python boolean replacements"""
    val = os.environ.get(key, default)
    if val == "True":
        val = True
    elif val == "False":
        val = False
    return val
