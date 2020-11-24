try:
    # Особенность запуска тестов в Visual Studio Code
    import os
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    django.setup()

    from django.test.utils import setup_test_environment
    setup_test_environment()
except:
    pass


from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question
from polls.models import Choice

def create_question(question_text, days):
    """
    Создаёт один вопрос
    """
    time = timezone.now() + timezone.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Очищаем тестовую базу данных
        # почему-то тестовая база берёт значения из основной
        Question.objects.all().delete()
        Choice.objects.all().delete()

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_past_question(self):
        """
        Вопрос созданный в прошлом отображается на главной странице вопрсов
        """
        q_id = create_question(question_text='Past question.', days=-30).id
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )
        q = response.context['latest_question_list'][0]
        self.assertEqual(q.id, q_id)
    
    def test_future_question(self):
        """
        Вопросы с датой публикации - будущее время, не должны
        отображаться на странице
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Даже если в базе есть вопросы в будущем и в прошлом времени,
        то должны отображаться только вопросы из прошлого
        """
        create_question(question_text='Past question.', days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_question(self):
        """
        Страница index может отбражать несколько тестов из прошлого
        """
        create_question(question_text='Past question 1.', days=-30)
        create_question(question_text='Past question 2.', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']

        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """Страница детализации вопроса с датой публикации в будущем возвращает 404"""
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        """
        Страница детализации вопроса с датой публикации в прошлом
        должна отображать текст вопроса
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
        

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() возвращает False для вопроса, который имеет pub_date - будущее время
        """
        time = timezone.now() + timezone.timedelta(days=30)
        future_question = Question(question_text='Абаракадабра?',pub_date=time)
        future_question.save()
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() возвращает False для вопросов, которым больше чем 1 день
        """
        time = timezone.now() - timezone.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() возвращает True для вопросов, которые не старше одного дня
        """
        time = timezone.now() - timezone.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
