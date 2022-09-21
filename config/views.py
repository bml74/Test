from django.http import JsonResponse
from django.shortcuts import render
from googletrans import Translator
from .utils import translate_phrase
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'market/index.html') 


def dashboard(request):
    return render(request, 'base/dashboard.html')


def search(request):
    return render(request, "search.html")


def chatbox_docs(request):
    return render(request, 'base/chatbox_docs.html')


def error_404_view(request, exception):
    status_number = "404"
    status_description = "The page you are looking for was not found."
    return render(request, 'errors/error.html', context={"status_number": status_number, "status_description": status_description}, status=404)


def ajax_chatbox(request):
    if request.method == 'POST':
        userMsg = request.POST.get('msg', '').lower().strip()

        fragments = userMsg.split() # ex. translate en > it hello world my name is Braeden
        if fragments[0] == "translate":
            if fragments[2] == ">":
                src = fragments[1]
                dest = fragments[3]
                """
                def translate_phrase(src="en", dest="en", phrase=""):
                    translator = Translator()
                    res = translator.translate(phrase, src=src, dest=dest)
                    return {"src": res.src, "dest": res.dest, "translated_text": res.text, "original_text": userMsg}

                """
                # translator = Translator()
                # res = translator.translate(" ".join(fragments[4:]), src=src, dest=dest)
                # translation_dict = {"src": res.src, "dest": res.dest, "translated_text": res.text, "original_text": userMsg}
                res = translate_phrase(src=src, dest=dest, phrase=" ".join(fragments[4:]))
                chatboxMsg = f"""
                Translation ({res['src'].upper()} to {res['dest'].upper()}):\n{res['translated_text']}
                """
                print(res)
                print(type(res))
        else:
            chatboxMsg = "Non capisco questa domanda...."

        if userMsg == "help":
            chatboxMsg = f"""
            1. Translation:<br><br><br>
            Format: 'translate SRC_LANG > DEST_LANG PHRASE'<br><br>
            Note: SRC_LANG and DEST_LANG use the two-letter codes. (For example, "en" or "es")<br><br>
            Example message: <strong>translate en > it mi chiamo Bruno</strong><br><br>
            Example response: <strong>my name is Bruno</strong><br><br>
            """

        chatbox_dict = {'userMsg': userMsg, 'chatboxMsg': chatboxMsg}

        return JsonResponse(chatbox_dict)

def vue_example(request):
    return render(request, 'asdf.html')
