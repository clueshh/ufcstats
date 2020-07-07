import re


def get_url_id(link):
    """
    Extracts the id from a url

    :param str link: the url to extract the id from
    :return: the url id
    """

    return link.split('/')[-1]


def split_name(fullname):
    """
    Splits a full name into two parts from the first space

    :param str fullname:
    :return:
    """
    return fullname.strip().split(' ', 1)


def re_compile(s):
    """
    Compiles a regex string ignoring the case

    :param str s: a regex string to search for
    :return re.compile: the compiled regex with re.IGNORECASE
    """

    return re.compile(s, re.IGNORECASE)
