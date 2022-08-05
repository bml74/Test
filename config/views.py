from urllib import response
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


def index(request):
    return render(request, 'base/index.html')


def dashboard(request):
    return render(request, 'base/dashboard.html')

def ajax_test_view(request):
    if request.method == 'POST':
        userMsg = request.POST.get('msg', '')
        print(f"User message: {userMsg}")
        chatboxMsg = "Mi chiamo Bruno" if userMsg == "Come ti chiami?" else "Non capisco questa domanda...."
        chatbox_dict = {'userMsg': userMsg, 'chatboxMsg': chatboxMsg}
        print(chatbox_dict)
        return JsonResponse(chatbox_dict)
