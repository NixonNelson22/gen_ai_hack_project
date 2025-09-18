from python_a2a import HTTPClient
import httpx
client = HTTPClient("http://localhost:5000/a2a")
response = client.send_message("constraint_server", "50")
print(response.content)
