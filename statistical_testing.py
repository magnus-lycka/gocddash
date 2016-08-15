from scipy.stats import mannwhitneyu


def mann_whitneyu_test(x, y):
    """
    Performs a mann_whitney statistical test on the two arrays
    :param x: one-dimensional array (length n)
    :param y: one-dimensional array (length n)
    """
    print(mannwhitneyu(x, y))


if __name__ == '__main__':
    pass
    # feature_data = create_agent_html_graph("~/GO_CSV/feature-tests.csv", "Feature-tests")
    # mann_whitneyu_test(characterize_data['result'], feature_data['result'])