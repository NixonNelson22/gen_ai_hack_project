from python_a2a import A2AServer, skill, run_server, agent


@agent(
    name="Main Agent",
    description="main administrative agent"
)
class MainAgent(A2AServer):
    @skill(name="constraint_server")
    def constraint(self, value):
        return {"temp_limit": value}


if __name__ == "__main__":
    main_agent = MainAgent(url="http://localhost:5000")
    run_server(main_agent, port=5000)
