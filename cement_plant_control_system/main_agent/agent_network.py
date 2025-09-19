from python_a2a import AgentNetwork
# Create a network of specialized agents
network = AgentNetwork(name="cement_optimizer_network")

# Add agents to the network with role names
network.add("main_agent", "http://localhost:5000")
network.add("fuel_agent", "http://localhost:5001")

# Create a client that can access the network
# client = HTTPClient(network)
#
# # The client can now interact with any agent in the network
# weather_response = client.send_message_to("weather", "What's the weather in Paris?")
# print(f"Weather: {weather_response.content}")
#
# hotels_response = client.send_message_to("hotels", "Find hotels in Paris")
# print(f"Hotels: {hotels_response.content}")
