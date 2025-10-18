from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from datetime import datetime
from .models import Sport, Booking, Player
from .forms import SignUpForm

# 🏠 Home Page
def home(request):
    sports = Sport.objects.all()
    return render(request, 'home.html', {'sports': sports})


# 🏏 Book a Sport
@login_required
def book_sport(request, sport_id):
    sport = get_object_or_404(Sport, id=sport_id)

    if request.method == 'POST':
        date = request.POST['date']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

        # Check if slot already booked
        existing = Booking.objects.filter(
            sport=sport,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if existing.exists():
            messages.error(request, "This time slot is already booked!")
            return redirect('home')

        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        duration = (end - start).seconds / 3600
        total_price = duration * float(sport.price_per_hour)

        booking = Booking.objects.create(
            sport=sport,
            user=request.user,
            date=date,
            start_time=start_time,
            end_time=end_time,
            total_price=total_price,
            status='Confirmed'
        )
        messages.success(request, "Booking successful! Now add your players.")
        return redirect('add_players', booking_id=booking.id)

    return render(request, 'book.html', {'sport': sport})


# 📅 My Bookings
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date')
    for booking in bookings:
        booking.player_count = Player.objects.filter(booking=booking).count()
        booking.players = Player.objects.filter(booking=booking)
    return render(request, 'my_bookings.html', {'bookings': bookings})


# 🧑‍🤝‍🧑 Add Players Page
@login_required
def add_players(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        names = request.POST.getlist('name')
        emails = request.POST.getlist('email')

        added_count = 0
        for n, e in zip(names, emails):
            if n.strip() and e.strip():
                # ✅ Player model will automatically create User
                Player.objects.create(
                    booking=booking,
                    name=n.strip(),
                    email=e.strip(),
                    status='Out'
                )
                added_count += 1

        messages.success(request, f"{added_count} players added successfully!")
        return redirect('my_bookings')

    return render(request, 'add_players.html', {'booking': booking})


# 📲 Player Details (Shows QR Code + Manual Toggle)
@login_required
def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    # Generate QR code safely via model method
    qr_image_base64 = player.get_qr_code_base64(request)

    if request.method == 'POST':
        player.status = 'In' if player.status == 'Out' else 'Out'
        player.save()
        messages.info(request, f"Player {player.name} is now marked as {player.status}.")
        return redirect('player_detail', player_id=player.id)

    return render(request, 'player_detail.html', {
        'player': player,
        'qr_image_base64': qr_image_base64
    })


# 🔄 QR Code Scan Toggle (Automatic In/Out)
def player_qr_toggle(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    player.status = 'In' if player.status == 'Out' else 'Out'
    player.save()
    messages.success(request, f"{player.name} marked as {player.status} via QR scan!")
    return redirect('player_detail', player_id=player.id)


# 🧾 Signup Page
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# 🚪 Logout
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')
