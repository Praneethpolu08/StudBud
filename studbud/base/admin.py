from django.contrib import admin
from .models import Room, Topic, Message,User

# Register Topic and Message as usual
admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Message)

# Custom admin for Room
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    filter_horizontal = ('participants',)  # ✅ Just use the field name here
