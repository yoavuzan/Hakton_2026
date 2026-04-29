from BackEnd.core.config import client

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Say hello in Hebrew"
)

print(response.output[0].content[0].text)