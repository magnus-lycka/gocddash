from bs4 import BeautifulSoup

from gocddash.analysis.go_client import go_request_comparison_html
from gocddash.util.html_utils import *


def open_html(pipeline_name, current, comparison):
    html = go_request_comparison_html(pipeline_name, current, comparison)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def fetch_pipeline_from_url(url):
    return url.rsplit("/", 1)[1] if "/" in url else url


def extract_list_of_lists_from_html_table(git_sections):
    final_list = []

    for table in git_sections:
        revisions = []
        modified_by = []
        comments = []

        git_url = (table.split("<strong>")[1]).split(",")[0]
        pipeline_name = fetch_pipeline_from_url(git_url)

        list_of_words = table.split()
        indices = [i for i, x in enumerate(list_of_words) if x == """class="revision">"""]
        for index in indices:
            revisions.append(clean_html(list_of_words[index + 1]))

        start_indices = [i for i, x in enumerate(list_of_words) if x == """class="modified_by">"""]
        end_indices = [i-1 for i, x in enumerate(list_of_words) if """class="comment"><p>""" in x]

        for i, index in enumerate(indices):
            modified_by.append(clean_html(' '.join(list_of_words[start_indices[i] + 1:end_indices[i]])))

        start_indices = [i for i, x in enumerate(list_of_words) if
                         """class="comment"><p>""" in x]  # Every comment starts with this
        end_indices = [i for i, x in enumerate(list_of_words) if "</td></tr>" in x]  # Every comments ends with this

        for i, index in enumerate(start_indices):
            comments.append((clean_html(' '.join(list_of_words[index:end_indices[i]]))).split(">")[1])

        for i, revision in enumerate(revisions):
            final_list.append([pipeline_name, git_url, revision, modified_by[i], comments[i]])

    return final_list


def get_git_comparison(pipeline_name, current, comparison):
    soup = open_html(pipeline_name, current, comparison)

    table = soup.find('div', {"style": "padding: 1em;"})
    unicode_table = [str(item) for item in table]
    git_sections = []
    for item in unicode_table:
        cleaned_text = remove_new_line(remove_excessive_whitespace(item))
        if cleaned_text:  # There are empty lines in the cleaned text for some reason
            git_sections.append(cleaned_text)

    git_sections = [item for item in git_sections if "Git" in item]

    final_list = extract_list_of_lists_from_html_table(git_sections)

    final_list = only_real_people(final_list)
    final_list = put_current_pipeline_at_top(final_list, pipeline_name)

    return final_list


def put_current_pipeline_at_top(git_blame_list, pipeline_name):
    sorted_list = sorted(git_blame_list, key=lambda x: pipeline_name not in x[
        0])  # Not all pipeline names are the same as their git repo names. Possible fix is to do NLP similarity comparisons.
    return sorted_list


def only_real_people(git_blame_list):
    return [item for item in git_blame_list if "go-agent" not in item[3]]
