from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Order, Profile, Review
from .forms import OrderForm

def index(request):
    orders = Order.objects.filter(status='open').order_by('-created_at')
    form = OrderForm()
    # Убрали top_mentors отсюда, так как в сайдбаре теперь просто ссылка
    context = {
        'orders': orders, 
        'form': form,
    }
    return render(request, 'app/index.html', context)

# НОВАЯ СТРАНИЦА: Список всех менторов
def mentors_list(request):
    mentors = Profile.objects.filter(is_mentor=True).order_by('-rating', '-deals_completed')
    return render(request, 'app/mentors_list.html', {'mentors': mentors})

@login_required
def user_detail(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect('profile')
    
    reviews = Review.objects.filter(target=target_user).order_by('-created_at')
    
    return render(request, 'app/user_detail.html', {
        'target_user': target_user,
        'profile': target_user.profile,
        'reviews': reviews
    })

@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.student = request.user
            order.save()
            messages.success(request, "Заказ успешно опубликован!")
    return redirect('index')

@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'open' or order.student == request.user:
        messages.error(request, "Ошибка принятия заказа.")
        return redirect('index')
    
    try:
        with transaction.atomic():
            customer_profile = order.student.profile
            if customer_profile.balance < order.price:
                messages.error(request, "У заказчика не хватает денег.")
                return redirect('index')
            
            customer_profile.balance -= order.price
            customer_profile.save()
            
            order.status = 'in_progress'
            order.executor = request.user
            order.save()
            messages.success(request, "Вы приняли заказ!")
    except Exception as e:
        messages.error(request, f"Ошибка: {e}")
    return redirect('index')

@login_required
def submit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, executor=request.user, status='in_progress')
    order.status = 'waiting_review'
    order.save()
    messages.info(request, "Заказ отправлен на проверку.")
    return redirect('profile')

@login_required
def confirm_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, student=request.user, status='waiting_review')
    try:
        with transaction.atomic():
            executor_profile = order.executor.profile
            executor_profile.balance += order.price
            executor_profile.save()
            order.status = 'completed'
            order.save()
            messages.success(request, "Заказ завершен!")
    except Exception as e:
        messages.error(request, f"Ошибка: {e}")
    return redirect('profile')

@login_required
def leave_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='completed')
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        if request.user == order.student and not order.student_reviewed:
            target_user = order.executor
            order.student_reviewed = True
        elif request.user == order.executor and not order.executor_reviewed:
            target_user = order.student
            order.executor_reviewed = True
        else:
            return redirect('profile')

        Review.objects.create(order=order, author=request.user, target=target_user, rating=rating, comment=comment)
        order.save()
        target_user.profile.update_rating()
        messages.success(request, "Отзыв оставлен!")
    return redirect('profile')

@login_required
def profile_view(request):
    my_orders = Order.objects.filter(student=request.user).order_by('-created_at')
    my_work = Order.objects.filter(executor=request.user).order_by('-created_at')
    return render(request, 'app/profile.html', {
        'my_orders': my_orders, 
        'my_work': my_work,
        'profile': request.user.profile,
    })

@login_required
def wallet_view(request):
    return render(request, 'app/wallet.html', {
        'profile': request.user.profile,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'app/register.html', {'form': form})