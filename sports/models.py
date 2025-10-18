from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse, NoReverseMatch
import qrcode
from io import BytesIO
from django.core.files import File
import base64

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

    @property
    def total_players(self):
        return self.player_set.count()

    @property
    def players_in(self):
        return self.player_set.filter(status='In').count()


# --- Player Model ---
class Player(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    status = models.CharField(max_length=10, default='Out')  # In / Out
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

    # ✅ Safe QR URL (won't break if URL not loaded)
    def get_qr_url(self):
        try:
            return reverse('toggle_player_status', args=[self.id])
        except NoReverseMatch:
            return None

    # ✅ Generate QR code as ImageField (call manually)
    def generate_qr_code(self):
        qr_url = self.get_qr_url() or '#'
        data = f"Scan to mark {self.name} ({self.status}) -> {qr_url}"
        qr_img = qrcode.make(data)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        file_name = f'qr_{self.id}.png'
        self.qr_code.save(file_name, File(buffer), save=False)

    # ✅ Override save() to create a user automatically
    def save(self, *args, **kwargs):
        creating = self._state.adding  # check if player is newly created
        super().save(*args, **kwargs)

        # Create a corresponding Django User only when a new player is added
        if creating and not self.user:
            username = self.name.strip()
            base_username = username
            counter = 1

            # Avoid duplicate usernames
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            new_user = User.objects.create_user(
                username=username,
                email=self.email,
                password="redball"
            )
            self.user = new_user
            super().save(update_fields=['user'])

    # Optional: generate base64 QR for templates without saving file
    def get_qr_code_base64(self, request=None):
        qr_url = self.get_qr_url() or '#'
        if request:
            qr_url = request.build_absolute_uri(qr_url)
        qr_img = qrcode.make(f"Scan to mark {self.name} ({self.status}) -> {qr_url}")
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
