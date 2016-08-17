import html
import re


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext)


def remove_excessive_whitespace(string):
    return re.sub(' ( )+', '', string)


def remove_wbr_tags(string):
    test = re.sub('<wbr>', '', string)
    test = re.sub('<wbr/>', '', test)
    test = re.sub('</wbr>', '', test)
    test = re.sub('<br/>', ' ', test)
    return test


def remove_new_line(string):
    return string.replace("\n", "")
