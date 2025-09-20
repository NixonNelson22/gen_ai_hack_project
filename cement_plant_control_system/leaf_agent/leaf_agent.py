from python_a2a import A2AServer, skill, run_server, agent, Message
from python_a2a.client import http

client = http.A2AClient("http://localhost:5000")
response = client.send_message(message)
print(response.content)


Leaf_agent = {}
