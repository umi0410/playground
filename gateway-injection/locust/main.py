from locust import task, FastHttpUser

class User(FastHttpUser):
    @task
    def index(self):
        response = self.client.get("/")