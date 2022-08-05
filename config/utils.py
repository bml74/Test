import imp
from googletrans import Translator


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def translate_phrase(src="en", dest="en", phrase=""):
    translator = Translator()
    res = translator.translate(phrase, src=src, dest=dest)
    return {"src": res.src, "dest": res.dest, "translated_text": res.text, "original_text": phrase}