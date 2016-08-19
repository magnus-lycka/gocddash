import html
import re


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext)


def remove_excessive_whitespace(string):
    return re.sub(' ( )+', '', string)


def remove_new_line(string):
    return string.replace("\n", "")
