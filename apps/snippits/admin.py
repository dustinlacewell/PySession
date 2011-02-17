from django.contrib.admin import TabularInline, ModelAdmin

class SnippitAdmin(ModelAdmin):
    list_display = ('timestamp', 'nickname', 'channel')




