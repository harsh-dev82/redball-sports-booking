from django.contrib import admin
from .models import Sport, Booking, Player

# ✅ Custom Admin Titles
admin.site.site_header = "RedBall Sports Admin"
admin.site.site_title = "RedBall Sports Booking"
admin.site.index_title = "Welcome to RedBall Management Panel"

# ✅ Register Models
admin.site.register(Sport)
admin.site.register(Booking)
admin.site.register(Player)
