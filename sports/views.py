from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import Sport, Booking, Player
from datetime import datetime
from .forms import SignUpForm


# 🏠 Home Page
def home(request):
    sports = Sport.objects.all()
    return render(request, 'home.html', {'sports': sports})


# 🏏 Book Sport
@login_required
def book_sport(request, sport_id):
    sport = get_object_or_404(Sport, id=sport_id)

    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        # 🔒 Prevent double-booking for the same time
        existing = Booking.objects.filter(
            sport=sport, date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if existing.exists():
            messages.error(request, "This slot is already booked!")
            return redirect('home')

        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        duration = (end - start).seconds / 3600
        total_price = duration * float(sport.price_per_hour)

        Booking.objects.create(
            sport=sport,
            user=request.user,
            date=date,
            start_time=start_time,
            end_time=end_time,
            total_price=total_price,
            status='Confirmed'
        )
        messages.success(request, "Booking successful! Now add your players.")
        return redirect('my_bookings')

    return render(request, 'book.html', {'sport': sport})


# 📅 My Bookings
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'my_bookings.html', {'bookings': bookings})


# 🧑‍🤝‍🧑 Add Players
@login_required
def add_players(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        names = request.POST.getlist('name')
        emails = request.POST.getlist('email')

        for n, e in zip(names, emails):
            user, created = User.objects.get_or_create(username=e, email=e)
            if created:
                user.set_password('redball')
                user.save()
            Player.objects.create(booking=booking, name=n, email=e)

        messages.success(request, "Players added successfully!")
        return redirect('my_bookings')

    return render(request, 'add_players.html', {'booking': booking})


# 📲 Player Details + QR Status
@login_required
def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if request.method == 'POST':
        player.status = 'In' if player.status == 'Out' else 'Out'
        player.save()
        messages.info(request, f"Player {player.name} is now marked as {player.status}.")
    return render(request, 'player_detail.html', {'player': player})


# 🧾 User Signup
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# 🚪 Custom Logout View (Fixes HTTP 405 error)
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')
