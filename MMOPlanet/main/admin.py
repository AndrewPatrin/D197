from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.text import format_lazy
from django_summernote.admin import SummernoteModelAdmin

from .models import Category, Post, Comment


class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    filter_horizontal = ('category',)
    # prepopulated_fields = {"post_slug": ("title",)}

    def formfield_for_manytomany(self, db_field, request, **kwargs):

        if db_field.name == 'category':
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name, is_stacked=False
            )
        else:
            return super().formfield_for_manytomany(db_field, request, **kwargs)
        if 'queryset' not in kwargs:
            queryset = Category.objects.all()
            if queryset is not None:
                kwargs['queryset'] = queryset
        form_field = db_field.formfield(**kwargs)
        msg = 'Hold down “Control”, or “Command” on a Mac, to select more than one.'
        help_text = form_field.help_text
        form_field.help_text = (
            format_lazy('{} {}', help_text, msg) if help_text else msg
        )
        return form_field

# class PostCategoryInline(admin.TabularInline):
#     model = PostCategory
#     fields = ['category']
#     extra = 0
#
# class PostAdmin(admin.ModelAdmin):
#     inlines = (PostCategoryInline,)
#     filter_horizontal = ['category']

admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)