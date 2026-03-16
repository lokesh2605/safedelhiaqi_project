from google import genai

client = genai.Client(api_key="AIzaSyB4A-XMPLCPcZOmmy_HwB8O6BvaCIvmUWU")

response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents="Say hello"
)

print(response.text)