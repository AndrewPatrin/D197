import thumbnail as thumbnail
from django.utils.safestring import mark_safe
from django_summernote.widgets import SummernoteWidget
from django import forms
from .models import Post, Comment


class ImagePreviewWidget(forms.widgets.FileInput):
    def render(self, name, value, attrs=None, **kwargs):
        input_html = super().render(name, value, attrs=None, **kwargs)
        img_html = mark_safe(f'<br><br><img src="/posts{value.url}"  width="300" height="200"/>')
        print(value.url)
        return f'{input_html}<br>{img_html}'


class PostEditForm(forms.ModelForm):
    content = forms.CharField(widget=SummernoteWidget)
    image = forms.ImageField(widget=ImagePreviewWidget)
    # image = forms.ImageField(widget=ImageWidget)

    class Meta:
        model = Post
        fields = [
            'image',
            'title',
            'subtitle',
            'category',
            'content',
        ]


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=SummernoteWidget)
    image = forms.ImageField()
    # image = forms.ImageField(widget=ImageWidget)
    class Meta:
        model = Post
        fields = [
            'image',
            'title',
            'subtitle',
            'category',
            'content',
        ]


class CommentForm(forms.ModelForm):
    comment_text = forms.CharField(
        max_length=100, widget=forms.Textarea(
            attrs={"rows": 3, "cols": 50, 'class': 'form-control', 'placeholder': 'Leave your comment here'}), label="")

    class Meta:
        model = Comment
        fields = [
            'comment_text',
        ]


class SubscribeForm(forms.Form):
    name = forms.CharField(max_length=100)
    rpath = forms.CharField(max_length=100)
    """class Meta:
        model = Category
        fields = [
            '',
        ]"""