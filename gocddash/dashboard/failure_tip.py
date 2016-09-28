"""Used for generating failure recommendations on the Insights page of the dashboard"""


def get_failure_tip(current, previous, last_success):
    if current.is_success():
        return "All good.", ""
    else:
        return handle_failure(current, previous, last_success)


def handle_failure(current, previous, last_success):
    last_claim = ""
    if previous and current:
        if previous.stage.description and previous.stage.responsible:
            last_claim = "Last claim: {}: {}".format(previous.stage.responsible, previous.stage.description)
    if current.stage.failure_stage == "POST":
        return "All tests passed, but the build failed.", last_claim
    elif current.stage.failure_stage == "STARTUP":
        return "Tests failed during STARTUP.", last_claim
    else:
        return handle_test_failure(current, previous, last_success), last_claim


def handle_test_failure(current, previous, last_success):
    failure_recommendation = FailureRecommendation(current, previous, last_success)
    if failure_recommendation.initial_tip_available():

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

        self.statistics_actions = [(
            lambda: self.current.stage.failure_stage == "STARTUP" and
                    self.current.stage.failure_stage == self.previous.stage.failure_stage,
            "Tests have failed at STARTUP several times in a row. Recommend to rerun after investigation."), (
            lambda: len(self.current.test_names) == 1 and 1 in current.test_names,  # Very specific for characterize
            "Recommend to rerun."), (
            lambda: self.current.failure_signature == self.previous.failure_signature and
                    self.current.test_names == self.previous.test_names,
            "Same failure signature and same failure indices as last failure."), (
            lambda: self.current.failure_signature == self.previous.failure_signature,
            "Same failure signature as last test. Unlikely flickering."), (
            lambda: self.current.test_names == self.previous.test_names,
            "Same failure indices as last test. Unlikely flickering."), (
            lambda: len(current.test_names) == 1,
            "Only one test failure. Potential for flickering but needs further investigation."), (
            lambda: len(self.current.test_names) == len(self.previous.test_names),
            "Same number of failures as previous test. Unlikely flickering.")
        ]

        self.fallback_actions = [(
            lambda: self.previous.is_success(),
            "Last pipeline was a success. Potential for flickering but may need further investigation."), (
            lambda: self.current.stage.pipeline_counter - last_success >= 3,
            "Pipeline hasn't been green in a long time."),
        ]

        self.default = "Last pipeline was a failure. Further investigation is recommended."

    def get_initial_recommendation(self):
        statistics_match = self.any_match()
        if statistics_match:
            return statistics_match

    def get_fallback_recommendation(self):
        return self.pick_match()

    def any_match(self):
        for predicate, string in self.statistics_actions:
            if predicate():
                return string

    def pick_match(self):
        for predicate, string in self.fallback_actions:
            if predicate():
                return string

        return self.default

    def initial_tip_available(self):
        return (self.current.has_error_statistics() and
                not self.previous.is_success() and
                self.previous.has_error_statistics())
