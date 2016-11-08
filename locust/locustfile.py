from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    def on_start(self):
        pass

    @task(10)
    def index(self):
        self.client.get("/?which=failing")
        self.__get_static()

    @task(5)
    def index_all(self):
        self.client.get("/?which=all")
        self.__get_static()

    @task(1)
    def stats(self):
        self.client.get("/stats")
        self.__get_static()
        self.client.get("/agents/success_rate/0/0/percent/*")

    @task(1)
    def insights(self):
        self.client.get("/insights/po-characterize-tests")
        self.__get_static()

    @task(1)
    def graph(self):
        self.client.get("/graphs/po-characterize-tests")
        self.__get_static()
        self.client.get("/pipelines/po-characterize-tests/history")
        self.client.get("/agents/success_rate/30/0/percent/po-characterize-tests")

    def __get_static(self):
        for url in [
            "http://go.pagero.local/dashtest/static/dash.css",
            "http://go.pagero.local/dashtest/static/plotly-latest.min.js",
            "http://go.pagero.local/dashtest/static/dash.js",
            "http://go.pagero.local/dashtest/static/index.js",
        ]:
            self.client.get(url)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 10000
    max_wait = 60000
