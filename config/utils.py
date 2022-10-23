import sys
from googletrans import Translator


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def translate_phrase(src="en", dest="en", phrase=""):
    translator = Translator()
    res = translator.translate(phrase, src=src, dest=dest)
    return {"src": res.src, "dest": res.dest, "translated_text": res.text, "original_text": phrase}

def GET_BASE_URL():
    DEBUG = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')
    if DEBUG:
        return 'http://127.0.0.1:8000'
    return 'https://cadebruno.com'


