from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import (
    Category, 
    Field, 
    Specialization,
    Course,
    Module, 
    Submodule, 
    Assignment,
    Task,
    AssignmentNote
)
import wikipedia, wikipediaapi
from googletrans import Translator
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from config.utils import is_ajax
from news.utils import get_languages
from pytube import Playlist, YouTube, extract
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup as bs
from strfseconds import strfseconds



def toggle_complete(request, id):
    obj = get_object_or_404(Assignment, id=id)
    if obj.completed.filter(id=request.user.id).exists():
        obj.completed.remove(request.user)
    else: 
        obj.completed.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def get_assignment_details(playlist_or_video_within_playlist_URL):
    p = Playlist(playlist_or_video_within_playlist_URL)
    watch_urls = p.video_urls
    assignments = []
    for watch_url in watch_urls:
        u = YouTube(url=watch_url)
        try:
            video_length = float(round(u.length / 60))
        except:
            video_length = 30.0
        video_id = extract.video_id(watch_url)
        embed_url = f"https://youtube.com/embed/{video_id}"
        assignments.append(
            {
                "embed_url": embed_url,
                "watch_url": watch_url,
                "title": u.title,
                "description": u.description,
                "video_length": video_length,
                "assignment_type": "Youtube Video Link"
            }
        )
    return assignments

def playlist_convert(request):
    if request.method == "POST":
        data = request.POST
        playlistLink = str(data.get("playlistLink"))
        submoduleID = int(data.get("submoduleID"))
        print(playlistLink)
        print(submoduleID)

        assignments = get_assignment_details(playlistLink)

        # Save to DB
        u = request.user
        # sm = Submodule.objects.filter(title="Introduction to Ancient Greek History with Donald Kagan")[0]
        sm = get_object_or_404(Submodule, id=submoduleID)
        for assignment in assignments:
            a = Assignment(title=assignment['title'], description=assignment['description'], assignment_type=assignment['assignment_type'], youtube_video_link=assignment['embed_url'], submodule=sm, estimated_minutes_to_complete=assignment['video_length'])
            # if assignment['transcript']:
            #     a = Assignment(title=assignment['title'], description=assignment['description'], assignment_type=assignment['assignment_type'], youtube_video_transcript_id=assignment['transcript'], submodule=sm, estimated_minutes_to_complete=assignment['video_length'])
            # else:
            #     a = Assignment(title=assignment['title'], description=assignment['description'], assignment_type=assignment['assignment_type'], youtube_video_link=assignment['embed_url'], submodule=sm, estimated_minutes_to_complete=assignment['video_length'])
            a.save()

        print("Added.")

        # HTTP Method POST. That means the form was submitted by a user
        # and we can find her filled out answers using the request.POST QueryDict
    else:
        print(request)
        pass
        # Normal GET Request (most likely).
        # We should probably display the form, so it can be filled
        # out by the user and submitted.
    return render(request, 'ecoles/playlist_convert.html')


class AssignmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Assignment
    template_name = 'ecoles/assignments/assignment_list_view.html'
    context_object_name = 'items'

    def test_func(self):
        # Check if user enrolled in the course.
        assignment = Assignment.objects.filter(id=self.kwargs['pk'])[0]
        submodule = assignment.submodule
        module = submodule.module
        course = module.course
        return self.request.user in course.students.all() or self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(AssignmentListView, self).get_context_data(**kwargs)
        submodule = get_object_or_404(Submodule, id=self.kwargs.get('submodule_id'))
        module = submodule.module
        course = module.course
        title = "Assignments | " + submodule.title + " | " + module.title + " | " + course.title
        context.update({"obj_type": "assignment", "title": title, "header": title, "course": course, "module": module, "submodule": submodule})
        return context

    def test_func(self):
        # Check if user enrolled in the course.
        submodule = Submodule.objects.filter(id=self.kwargs['submodule_id'])[0]
        course = submodule.module.course
        return self.request.user in course.students.all()


class AssignmentDetailView(UserPassesTestMixin, DetailView):
    model = Assignment

    def test_func(self):
        # Check if user enrolled in the course.
        assignment = Assignment.objects.filter(id=self.kwargs['pk'])[0]
        submodule = assignment.submodule
        module = submodule.module
        course = module.course
        return self.request.user in course.students.all() or self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get(self, request, *args, **kwargs):

        assignment = get_object_or_404(Assignment, pk=kwargs['pk'])
        assignment_completed = assignment.completed.filter(id=request.user.id).exists()
        submodule = get_object_or_404(Submodule, pk=assignment.submodule.id)
        module = get_object_or_404(Module, pk=submodule.module.id)
        course = get_object_or_404(Course, pk=module.course.id)
        allowed_to_edit = request.user in course.allowed_editors.all()
        specialization = course.specialization

        try:
            field = get_object_or_404(Field, pk=course.field.id); category = get_object_or_404(Category, pk=field.category.id)
        except AttributeError:
            field = None; category = None

        # tasks = Task.objects.filter(assignment=assignment) # ex. Read, Watch, Take Notes, etc.
        # user_tasks_completed_arr_of_arrs = [[task.id, str(task.completed.filter(id=request.user.id).exists())] for task in tasks]           
            
        # user_tasks_completed_arr_of_arrs = json.dumps(user_tasks_completed_arr_of_arrs) # Now JSON

        # all_tasks = Task.objects.all()
        # num_total_tasks = len(list(tasks))
        # if num_total_tasks > 0:
        #     last_task_id = list(all_tasks)[-1].id # Get ID of last object in Task model
        # else:
        #     last_task_id = None

        # task_choices_arr_of_tuples = Task.task_type.field.choices

        # # Progress bar:
        # total = 0
        # if assignment_completed: # assignment_completed = assignment.completed.filter(id=request.user.id).exists()
        #     total += 1
        # for user_defined_task in tasks: # tasks = Task.objects.filter(assignment=assignment)
        #     user_task_completed = request.user in user_defined_task.completed.all()
        #     if user_task_completed:
        #         total += 1
        # pct_completed = int((total / (num_total_tasks + 1)) * 100) # Add 1 because of the default task made by creator 



        if is_ajax(request=request):
            if request.GET.get('original_text'):
                original_text = request.GET.get('original_text')
                src = request.GET.get('src')
                dest = request.GET.get('dest')
                print(src)
                print(dest)
                print(original_text)
                translator = Translator()
                res = translator.translate(original_text, src=src, dest=dest)
                translation_dict = {"src": res.src, "dest": res.dest, "translated_text": res.text, "original_text": original_text}
                print(translation_dict)
                return JsonResponse(translation_dict)
            if request.GET.get('wiki_query'):
                wiki_query = request.GET.get('wiki_query')
                lang = request.GET.get('lang')
                # suggestion = wikipedia.suggest(wiki_query)
                results = wikipedia.search(wiki_query)
                print(results)
                first_result = results[0]
                try:
                    wikipedia.set_lang(lang)
                    pg = wikipedia.page(first_result)
                    first_result_title = pg.title
                    wiki_page_url = pg.url
                    summ = wikipedia.summary(first_result) # Additional parameter: sentences=2
                except:
                    try:
                        wiki_wiki = wikipediaapi.Wikipedia(language=lang)
                        pg = wiki_wiki.page(first_result)
                        first_result_title = pg.title
                        summ = pg.summary
                        wiki_page_url = pg.fullurl
                    except:
                        wiki_page_url, summ, first_result_title = "", "", ""
                wiki_dict = {
                    "results": results,
                    "wiki_page_url": wiki_page_url,
                    "summary": summ,
                    "first_result_title": first_result_title
                }
                return JsonResponse(wiki_dict)
            if request.GET.get('user_note_title') or request.GET.get('user_note_text'):
                title = request.GET.get('user_note_title')
                text = request.GET.get('user_note_text')
                try:
                    updated_note = AssignmentNote.objects.filter(assignment=assignment).filter(creator=self.request.user).first()
                    updated_note.title = title
                    updated_note.content = text
                    updated_note.save()
                except AttributeError: # If AttributeError, then note didn't exist, and we have to create one rather than updating it.
                    new_note = AssignmentNote(creator=self.request.user, assignment=assignment, title=title, content=text)
                    new_note.save()
                return JsonResponse({'user_note_title_updated': title, 'user_note_text_updated': text})



        context = {
            "obj_type": "assignment", 
            "item": assignment, 
            "assignment": assignment,
            "allowed_to_edit": allowed_to_edit,
            "assignment_completed": assignment_completed,
            # "user_tasks_completed_arr_of_arrs": user_tasks_completed_arr_of_arrs,
            # "task_choices_arr_of_tuples": task_choices_arr_of_tuples,
            # "num_total_tasks": num_total_tasks,
            # "last_task_id": last_task_id,
            # "pct_completed": pct_completed,
            # "total": total,

            "category": category, 
            "field": field, 
            "specialization": specialization, 
            "course": course, 
            "module": module,
            "submodule": submodule, 
            # "tasks": tasks,

            'LANGUAGES': get_languages()


        }


        # Get assignment note if it exists:
        try:
            assignment_note = AssignmentNote.objects.filter(assignment=assignment).filter(creator=self.request.user).first()
            context.update({"assignment_note": assignment_note})
        except AttributeError:
            context.update({"assignment_note": None})

        if assignment.assignment_type == "Youtube Video Transcript ID":
            video_id = assignment.youtube_video_transcript_id
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            doc = requests.get(video_url)
            soup = bs(doc.content, 'html.parser')
            video_title = soup.title.get_text()
            transcript_full = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_for_display = [[strfseconds(seconds=int(arr['start'])).split('.')[0], arr['text']] for arr in transcript_full]
            video_details = {"video_id": video_id, "transcript_for_display": transcript_for_display, "video_title": video_title}
            context.update(video_details)
        elif assignment.assignment_type == "Article":
            article_by_url = assignment.article_by_url
            article_id = assignment.article_id

        if is_ajax(request):
            toggle_completed, user_toggle_completed, new_task = None, None, None

            toggle_completed = request.GET.get('toggle_completed')
            if toggle_completed:
                obj_instance = get_object_or_404(Assignment, pk=kwargs['pk'])
                if obj_instance.completed.filter(id=request.user.id).exists():
                    # User has already completed assignment. The following line makes it so user has not completed.
                    obj_instance.completed.remove(request.user)
                    obj_instance.save()
                    message = f"{request.user} has not completed assignment '{assignment.title}'"
                    a_completed = False
                else: # User completed assignment.
                    obj_instance.completed.add(request.user)
                    obj_instance.save()
                    message = f"{request.user} has completed assignment '{assignment.title}'"
                    a_completed = True
                return JsonResponse({"message": message, "a_completed": a_completed})

            # user_toggle_completed = request.GET.get('user_toggle_completed')
            # if user_toggle_completed:
            #     assignment_instance = get_object_or_404(Assignment, pk=kwargs['pk'])
            #     # tasks_within_assignment = assignment_instance.tasks_within_assignment.all() # Get all tasks with foreign key of the particular assignment

            #     print("\n\n\n\n\n\n\n")

            #     print(f"CP1: {assignment_instance}")

            #     # Get task instance:
            #     task_id = request.GET.get('task_id')
            #     task_instance = get_object_or_404(Task, pk=task_id)

            #     print(f"CP2: {task_id}")
            #     print(f"CP3: {task_instance}")
            #     print(task_instance.completed.filter(id=request.user.id).exists())
                
                # if task_instance.completed.filter(id=request.user.id).exists():
                #     # User has already completed task. The following line makes it so user has not completed.
                #     task_instance.completed.remove(request.user)
                #     task_instance.save()
                #     print(f"AAA")
                # else: # User completed task.
                #     task_instance.completed.add(request.user)
                #     task_instance.save()
                #     print(f"BBB")

                # print("\n\n\n\n\n\n\n")
            

            # new_task = request.GET.get('select_option_val_for_task')
            # if new_task:
            #     assignment_instance = get_object_or_404(Assignment, pk=kwargs['pk'])
            #     t = Task(task_type=new_task, assignment=assignment_instance)
            #     t.save()
            #     context.update({"new_id": t.id});
            #     print(f"{t.id} " * 50)
            #     return render(request, 'ecoles/assignments/assignment_detail_view.html', context)#return render(request, 'malagosto/ecole/assignment.html', context)
            
            return render(request, 'ecoles/assignments/assignment_detail_view.html', context)

        return render(request, 'ecoles/assignments/assignment_detail_view.html', context)#return render(request, 'malagosto/ecole/assignment.html', context)


class AssignmentCreateView(LoginRequiredMixin, CreateView):    
    model = Assignment
    fields = ['title', 'due_date', 'description', 'language', 'submodule', 'estimated_minutes_to_complete', 'assignment_type', 'text', 'internal_link', 'external_reading_link', 'external_link', 'iframe_link', 'youtube_video_link', 'youtube_video_transcript_id', 'corsican_bible_chapter', 'article_by_url', 'article_id']
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user is creator or an allowed editor.
        submodule = Submodule.objects.filter(id=self.kwargs['submodule_id'])[0]
        module = submodule.module
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(AssignmentCreateView, self).get_context_data(**kwargs)
        obj_type = "assignment"
        context.update({"obj_type": obj_type, "header": f"Create {obj_type}"})
        return context



class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assignment
    fields = ['title', 'due_date', 'description', 'language', 'submodule', 'estimated_minutes_to_complete', 'assignment_type', 'text', 'internal_link', 'external_reading_link', 'external_link', 'iframe_link', 'youtube_video_link', 'youtube_video_transcript_id', 'corsican_bible_chapter']
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user is creator or an allowed editor.
        submodule = Submodule.objects.filter(id=self.kwargs['submodule_id'])[0]
        module = submodule.module
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(AssignmentUpdateView, self).get_context_data(**kwargs)
        obj_type = "assignment"
        context.update({"obj_type": obj_type, "header": f"Update {obj_type}"})
        return context


class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Assignment
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = 'ecoles/confirm_delete_view.html'

    def test_func(self):
        # Check if user is creator or an allowed editor.
        submodule = Submodule.objects.filter(id=self.kwargs['submodule_id'])[0]
        module = submodule.module
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(AssignmentDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": "assignment"})
        return context