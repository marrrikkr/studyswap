from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

class Subject(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    telegram = models.CharField(max_length=100, blank=True, null=True, help_text="Ник в Telegram без @")
    
    # СТАТИСТИКА P2P
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    deals_completed = models.PositiveIntegerField(default=0)

    # НОВОЕ: СТРУКТУРА МЕНТОРА
    is_mentor = models.BooleanField(default=False, verbose_name="Статус ментора")
    is_verified = models.BooleanField(default=False, verbose_name="Проверенный")
    skills = models.CharField(max_length=200, blank=True, verbose_name="Навыки (через запятую)")
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")

    def update_rating(self):
        reviews = Review.objects.filter(target=self.user)
        if reviews.exists():
            avg = reviews.aggregate(Avg('rating'))['rating__avg']
            self.rating = round(avg, 2)
            self.deals_completed = reviews.count()
            self.save()

    def __str__(self): return f"Профиль {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Order(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('in_progress', 'В работе'),
        ('waiting_review', 'На проверке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_created')
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_executed')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    student_reviewed = models.BooleanField(default=False)
    executor_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject.name} ({self.status})"

class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_reviews')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"От {self.author.username} для {self.target.username} ({self.rating}★)"