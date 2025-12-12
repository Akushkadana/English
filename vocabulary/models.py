from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Word(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='words')
    english = models.CharField(max_length=100)
    russian = models.CharField(max_length=100)
    image = models.ImageField(upload_to='words/', blank=True, null=True)
    transcription = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.english} - {self.russian}"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    learned = models.BooleanField(default=False)  # нажал "Выучил"
    repetitions = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'word')

    def __str__(self):
        return f"{self.user} - {self.word.english} ({'выучено' if self.learned else 'в процессе'})"

class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()  # правильные ответы
    total = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.score}/{self.total} ({self.created_at.date()})"