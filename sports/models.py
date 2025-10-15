from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File

# --- Sport Model ---
class Sport(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    available_from = models.TimeField()
    available_to = models.TimeField()

    def __str__(self):
        return self.name


# --- Booking Model ---
class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.sport.name} - {self.date}"


# --- Player Model ---
class Player(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    status = models.CharField(max_length=10, default='Out')  # In / Out
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = f"Player: {self.name}, BookingID: {self.booking.id}"
        qr_img = qrcode.make(data)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        file_name = f'qr_{self.id}.png'
        self.qr_code.save(file_name, File(buffer), save=False)
        super().save(update_fields=['qr_code'])
