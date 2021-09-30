from locust import HttpUser, between, task

class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def main_page(self):
        self.client.get("/texts")
        self.client.get("/textsDetail/1")
