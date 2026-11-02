from locust import HttpUser, task, between


class ClimateTechAPIUser(HttpUser):
    wait_time = between(1, 3)

    def check_slow_request(self, response, endpoint):
        server_time = response.headers.get(
            "X-Process-Time-MS", "missing"
        )

        if response.elapsed.total_seconds() * 1000 > 500:
            print(
                f"SLOW REQUEST: {endpoint} | "
                f"Locust: {response.elapsed.total_seconds() * 1000:.2f} ms | "
                f"FastAPI: {server_time} ms"
            )

    @task(3)
    def get_assessment(self):
        with self.client.get(
            "/demo/assessment",
            name="/demo/assessment",
            catch_response=True,
        ) as response:
            self.check_slow_request(response, "/demo/assessment")

    @task(1)
    def health_check(self):
        with self.client.get(
            "/health",
            name="/health",
            catch_response=True,
        ) as response:
            self.check_slow_request(response, "/health")