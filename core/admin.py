# admin.py


from django.contrib import admin

from .models import EventRoom, EventStanding, School, TamsTeam


@admin.register(EventRoom)
class EventRoomAdmin(admin.ModelAdmin):

    list_display = ('event_name', 'room_code', 'is_active')
    list_filter = ('event_name', 'is_active')

    search_fields = ('room_code', 'event_name')

admin.site.register(School)
admin.site.register(TamsTeam)
admin.site.register(EventStanding)
