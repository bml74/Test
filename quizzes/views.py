from curses import A_ALTCHARSET
from django.shortcuts import render
from .models import Quiz, Result
from django.views.generic import ListView
from django.http import JsonResponse
from questions.models import Question, Answer
from config.utils import  is_ajax


class QuizListView(ListView):
    model = Quiz 
    template_name = 'quizzes/main.html'


def quiz_view(request, pk):
    quiz = Quiz.objects.get(pk=pk)
    return render(request, 'quizzes/quiz.html', {'obj': quiz})


def quiz_data_view(request, pk):
    quiz = Quiz.objects.get(pk=pk)
    questions = []
    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.text)
        questions.append({str(q): answers})
    return JsonResponse({
        'data': questions,
        'time': quiz.time,
    })


def save_quiz_view(request, pk):
    if is_ajax(request=request):
        questions = []
        data = request.POST
        data_ = dict(data.lists())

        data_.pop('csrfmiddlewaretoken')

        user = request.user
        quiz = Quiz.objects.get(pk=pk)
        
        for k in data_.keys():
            print('Key: ', k)
            question = Question.objects.filter(text=k).filter(quiz=quiz).first()
            questions.append(question)
        print(questions)

        score = 0
        multiplier = 100 / quiz.number_of_questions
        results = []
        correct_answer = None

        for q in questions:
            a_selected = request.POST.get(q.text)
            print(f"Selected: {a_selected}")

            if a_selected != "":
                question_answers = Answer.objects.filter(question=q)
                for a in question_answers:
                    if a_selected == a.text:
                        if a.correct:
                            score += 1
                            correct_answer = a.text
                    else:
                        if a.correct:
                            correct_answer = a.text

                results.append({str(q): {'correct_answer': correct_answer, 'answered': a_selected}})
            else:
                results.append({str(q): 'Not answered'})
            
        score_ = score * multiplier
        r = Result(quiz=quiz, user=user, score=score_); r.save()

        if score_ >= quiz.required_score_to_pass:
            return JsonResponse({'passed': True, 'score': score_, 'results': results})
        else:
            return JsonResponse({'passed': False, 'score': score_, 'results': results})
