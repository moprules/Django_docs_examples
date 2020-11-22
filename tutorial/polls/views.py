from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.views import generic

from .models import Question
from .models import Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Вернёт последние 5 публикованных вопросов"""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    context_object_name = 'q'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {
#         'latest_question_list': latest_question_list,
#     }
#     return render(request, "polls/index.html", context)

# def detail(request, question_id):
#     question = get_object_or_404(Question, id=question_id)
#     return render(request, "polls/detail.html", {'question': question})

# def results(request, question_id):
#     question = get_object_or_404(Question, id=question_id)
#     return render(request, "polls/results.html", {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    try:
        selected_choice=question.choice_set.get(id=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Показываем форму вопроса занаво с сообщение об ошибке
        context = {
            'question': question,
            'error_message': "You didn't select a choice"
        }
        return render(request, "polls/detail.html", context)
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))