from django.shortcuts import render
import openai
api_key = "YOUR_API_KEY"

client = openai.OpenAI(api_key=api_key)
def train(request):
    return render(request,"AI/discover.html")
def home(request):
    return render(request,"AI/home.html")
def index(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file_input")


        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Check if there are any proofs of any historical sites and get the rough estimates. Refer to all the available sources of the internet. Also check if it is a newly discovered historical site!"},

                    ],
                    "file": uploaded_file
                },
            ],

        )
        answer = response.choices[0].message.content.strip()
        return render(request, "AI/index.html", {"answer": answer})
    return render(request, "AI/index.html")