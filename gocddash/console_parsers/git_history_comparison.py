"""Fetches and builds the Git History Comparison list and sorts it by current pipeline name and preferred upstream
as specified in application.cfg. Filters out any material revision modifications by go-agent.

"""

# noinspection PyPackageRequirements
from bs4 import BeautifulSoup

from gocddash.analysis.go_client import go_request_comparison_html
from gocddash.util.html_utils import remove_new_line


def open_html(pipeline_name, current, comparison):
    html = go_request_comparison_html(pipeline_name, current, comparison)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def material_revision_diff_tests(soup):
    return "pipeline instance that was triggered with a non-sequential material revision." in str(soup)


def get_git_comparison(pipeline_name, current, comparison, preferred_upstream):
    """
    Extracts the git history comparison from the GO comparison HTML page and
    stores the data in the following data structure
    [(Git Name [(Revision, Modified By, Comment)]), etc...]
    :param pipeline_name: the name of the pipeline to get the git comparison for
    :param current: current pipeline counter
    :param comparison: comparison pipeline counter
    :param preferred_upstream: the preferred upstream pipeline to sort by
    :return: None if there is a material revision difference in GO. Otherwise, the data structure mentioned earlier.
    """
    soup = open_html(pipeline_name, current, comparison)

    if material_revision_diff_tests(soup):
        return None

    material_titles = soup.findAll('div', {"class": "material_title"})
    git_sections = list(
        map(lambda z: z.rpartition("/")[2],
            filter(lambda y: not y.startswith(" Pipeline"),
                   map(lambda x: x.findAll('strong')[0].get_text(),
                       material_titles)))
    )
    tables = soup.findAll('table', {'class': "list_table material_modifications"})

    changes = []
    for table_index, table in enumerate(tables):
        revisions = table.findAll('td', {'class': 'revision'})
        modified_by = table.findAll('td', {'class': 'modified_by'})
        comments = table.findAll('td', {'class': 'comment'})

        these_changes = []
        for index, revision in enumerate(revisions):
            revision_text = revision.get_text().strip()
            modified_by_text = remove_new_line(modified_by[index].get_text().strip())
            comments_text = comments[index].get_text().strip()
            these_changes.append((revision_text, modified_by_text, comments_text))

        these_changes = only_real_people(these_changes)
        if these_changes:  # Avoids adding an empty list to the go-agent revision pipelines that have been filtered out
            changes.append((git_sections[table_index], these_changes))

    changes = sort_by_current_then_preferred(changes, pipeline_name, preferred_upstream)
    return changes


def sort_by_current_then_preferred(git_history_list, pipeline_name, preferred_upstream):
    # Not all pipeline names are the same as their git repo names. Possible fix is to do NLP similarity comparisons.
    git_history_list.sort(
        key=lambda x: (pipeline_name not in x[0], preferred_upstream not in x[0]))  # x[0] is the pipeline column
    return git_history_list


def only_real_people(git_history_list):
    return list(filter(lambda x: "go-agent" not in x[1], git_history_list))
