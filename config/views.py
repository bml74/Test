# from turtle import title
import os
from django.http import JsonResponse
from django.shortcuts import render
from googletrans import Translator
from .utils import translate_phrase
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from ecoles.models import Category, Field, Specialization, Course
from market.models import Listing
from decouple import config
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



@login_required
def index(request):

    if request.user.username == "bml74":

        import google.oauth2.credentials
        import google_auth_oauthlib.flow
        import googleapiclient.discovery


        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Getting the upcoming 10 events')
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')
                return

            # Prints the start and name of the next 10 events
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])

        except HttpError as error:
            print(error)


    return render(request, 'market/index.html') 


def dashboard(request):
    return render(request, 'base/dashboard.html')


def search(request):
    return render(request, "search.html")


def search_results(request):
    if request.method == "GET":
        term = request.GET.get('term', None)
        if term: 
            user_results = User.objects.filter(username__icontains=term).all()
            group_results = Group.objects.filter(name__icontains=term).all()
            category_results = Category.objects.filter(title__icontains=term).all()
            field_results = Field.objects.filter(title__icontains=term).all()
            specialization_results = Specialization.objects.filter(title__icontains=term).all()
            course_results = Course.objects.filter(title__icontains=term).all()
            listing_results = Listing.objects.filter(title__icontains=term).all()
            context = {
                'term': term,
                "user_results": user_results,
                "group_results": group_results,
                "category_results": category_results,
                "field_results": field_results,
                "specialization_results": specialization_results,
                "course_results": course_results,
                "listing_results": listing_results,
            }
            return render(request, 'search_results.html', context)
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
            chatboxMsg = "Sorry, I don't understand this."

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
