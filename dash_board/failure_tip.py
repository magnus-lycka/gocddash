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
    failure_recommendation = FailureRecommendation(current, previous, last_success)
    if current.has_error_statistics() and not previous.is_success() and previous.has_error_statistics():

        if len(current.test_names) == 1:
            return "Only one test failure. Potential for flickering."

        initial_tip = failure_recommendation.get_initial_recommendation()
        if initial_tip:
            return initial_tip

    fallback_tip = failure_recommendation.get_fallback_recommendation()

    return fallback_tip


class FailureRecommendation:
    def __init__(self, current, previous, last_success):
        self.current = current
        self.previous = previous
        self.last_success = last_success

        # This is a bit hard to read
        self.statistics_actions = [
            (
            lambda: len(self.current.test_names) == 1 and 1 in current.test_names,  # Very specific for characterize
            "Flickering"),
            (lambda: self.current.failure_signature == self.previous.failure_signature and self.current.test_names == self.previous.test_names,
            "Same failure signature and same failure indices. Not flickering."),
            (lambda: self.current.failure_signature == self.previous.failure_signature,
             "Same failure signature as last test. Unlikely flickering."),
            (lambda: self.current.test_names == self.previous.test_names,
             "Same failure indices as last test. Unlikely flickering."),
            (lambda: len(current.test_names) == 1,
            "Only one test failure. Potential for flickering."),
            (lambda: len(self.current.test_names) == len(self.previous.test_names),
                         "Same number of failures as previous test. Unlikely flickering.")
        ]

        self.fallback_actions = [
            (lambda: self.previous.is_success(), "Last pipeline was a success. Suspected flickering."),
            (lambda: self.current.stage.pipeline_counter - last_success >= 3,
             "Pipeline hasn't been green in a long time. Fix it!"),
        ]

        self.default = "Last pipeline was a failure. Potential for flickering but more likely a real failure."

    def get_initial_recommendation(self):
        statistics_match = self.any_match(self.statistics_actions)
        if statistics_match:
            return statistics_match

    def get_fallback_recommendation(self):
        return self.pick_match(self.fallback_actions, self.default)

    def any_match(self, actions):
        for predicate, string in actions:
            if predicate():
                return string

        return None

    def pick_match(self, actions, default):
        for predicate, string in actions:
            if predicate():
                return string

        return default
