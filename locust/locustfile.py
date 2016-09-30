from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        pass

    @task(10)
    def index(self):
        self.client.get("/?which=failing")

    @task(5)
    def index_all(self):
        self.client.get("/?which=all")

    @task(1)
    def index_stats(self):
        self.client.get("/stats")
        self.client.get("/agents/success_rate/0/0/percent")


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
