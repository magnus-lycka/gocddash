def get_failure_tip(current, previous, last_success):
    if current.is_success():
        return "All good."
    else:
        return handle_failure(current, previous, last_success)


def handle_failure(current, previous, last_success):
    if current.stage.failure_stage == "POST":
        return "All tests passed, but the build failed."
    elif current.stage.failure_stage == "STARTUP":
        return "Tests failed during STARTUP."
    else:
        return handle_test_failure(current, previous, last_success)


# TODO: Really do something about the ordering here - maybe with composition of predicates.
def handle_test_failure(current, previous, last_success):
    if current.has_error_statistics() and not previous.is_success() and previous.has_error_statistics():
        if len(current.test_names) == 1 and 1 in current.test_names:
            return "Flickering"

        statistics_actions = [
            (lambda: current.failure_signature == previous.failure_signature and current.test_names == previous.test_names,
            "Same failure signature and same failure indices. Not flickering."),
            (lambda: current.failure_signature == previous.failure_signature,
             "Same failure signature as last test. Something something..."),
            (lambda: current.test_names == previous.test_names,
             "Same failure indices as last test. Something something...")
        ]

        statistics_match = any_match(statistics_actions)
        if statistics_match:
            return statistics_match

    actions = [
        (lambda: previous.is_success(), "Last pipeline was a success. Suspected flickering."),
        (lambda: current.stage.pipeline_counter - last_success >= 3,
         "Pipeline hasn't been green in a long time. Fix it!"),
    ]

    default = "Last pipeline was a failure. Potential for flickering but more likely a real failure."

    return pick_match(actions, default)


def any_match(actions):
    for predicate, string in actions:
        if predicate():
            return string

    return None


def pick_match(actions, default):
    for predicate, string in actions:
        if predicate():
            return string

    return default
