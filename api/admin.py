from django.contrib import admin
from .models import UserProfile,User,Post,Comment
# Register your models here.



admin.site.register(User)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user','first_name','last_name','gender','country')
    list_display_links = ('id','user')
    search_fields = ('first_name',) 

admin.site.register(UserProfile,ProfileAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = ('id','author','title')
    list_display_links = ('id','author')
    search_fields = ('title',) 

admin.site.register(Post,PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author','post')

admin.site.register(Comment,CommentAdmin)
