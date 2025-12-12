from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO

from .models import Category, Word, UserProgress, QuizResult
import random

def home(request):
    categories = Category.objects.all()
    return render(request, 'vocabulary/home.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    words = category.words.all()
    return render(request, 'vocabulary/category_detail.html', {
        'category': category,
        'words': words
    })


@login_required
def learn_word(request, word_id):
    word = get_object_or_404(Word, id=word_id)
    progress, created = UserProgress.objects.get_or_create(user=request.user, word=word)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "learned":
            progress.learned = True
        elif action == "repeat":
            progress.repetitions += 1
        progress.save()
        return redirect('vocabulary:category_detail', slug=word.category.slug)

    return render(request, 'vocabulary/learn_word.html', {'word': word, 'progress': progress})


@login_required
def quiz(request, slug):
    category = get_object_or_404(Category, slug=slug)
    words = list(category.words.all())

    if len(words) < 4:
        return render(request, 'vocabulary/quiz.html', {
            'error': 'В категории должно быть минимум 4 слова для теста.',
            'category': category
        })

    if request.method == "POST":
        score = 0
        total = 0
        for key, value in request.POST.items():
            if key.startswith('question_'):
                total += 1
                word_id = key.split('_')[1]
                word = Word.objects.get(id=word_id)
                if word.russian == value:
                    score += 1

        QuizResult.objects.create(
            user=request.user,
            score=score,
            total=total,
            category=category
        )
        return render(request, 'vocabulary/quiz_result.html', {'score': score, 'total': total})

    # Генерация вопросов
    questions = random.sample(words, min(10, len(words)))
    for q in questions:
        options = [q.russian]
        distractors = Word.objects.exclude(id=q.id).values_list('russian', flat=True)
        options += random.sample(list(distractors), min(3, len(distractors)))
        random.shuffle(options)
        q.options = options

    return render(request, 'vocabulary/quiz.html', {
        'category': category,
        'questions': questions
    })


@login_required
def profile(request):
    learned_count = UserProgress.objects.filter(user=request.user, learned=True).count()
    total_words = Word.objects.count()
    results = QuizResult.objects.filter(user=request.user).order_by('-created_at')[:10]

    return render(request, 'vocabulary/profile.html', {
        'learned_count': learned_count,
        'total_words': total_words,
        'results': results
    })


# ЭКСПОРТ В PDF
from xhtml2pdf import pisa
from django.conf import settings
import os

def link_callback(uri, rel):
    """
    Фикс для загрузки изображений из media и static
    """
    # Для static файлов
    if uri.startswith(settings.STATIC_URL):
        path = finders.find(uri.replace(settings.STATIC_URL, "", 1))
        if path:
            return path
    # Для media файлов
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, "").lstrip('/'))
        if os.path.isfile(path):
            return path
    # Если полный URL (http) — оставляем
    if uri.startswith("http"):
        return uri
    raise Exception(f"Файл не найден: {uri}")

@login_required
def export_pdf(request, slug):
    category = get_object_or_404(Category, slug=slug)
    words = category.words.all()

    template = get_template('vocabulary/pdf_template.html')
    html = template.render({'category': category, 'words': words, 'request': request})

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding="UTF-8", link_callback=link_callback)

    if pdf.err:
        return HttpResponse(f"Ошибка PDF: {pdf.err}", status=500)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{category.name}_cards.pdf"'
    return response
    return HttpResponse("Ошибка создания PDF", status=500)