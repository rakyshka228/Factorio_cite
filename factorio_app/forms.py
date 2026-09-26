from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
from uuid import uuid4

from .models import Blueprint, Comment, Tag


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label='Электронная почта')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
        }


class BlueprintForm(forms.ModelForm):
    tag_names = forms.CharField(
        required=False,
        label='Теги',
        help_text='Через запятую: поезда, нефть, наука',
    )

    class Meta:
        model = Blueprint
        fields = ('title', 'description', 'code', 'image')
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'code': 'Код чертежа',
            'image': 'Изображение превью',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'code': forms.Textarea(attrs={'rows': 8}),
        }

    def save(self, author, commit=True):
        blueprint = super().save(commit=False)
        blueprint.author = author
        blueprint.slug = f'{slugify(blueprint.title)}-{author.pk}-{uuid4().hex[:8]}'
        if commit:
            blueprint.save()
            self.save_tags(blueprint)
        return blueprint

    def save_tags(self, blueprint):
        tags = []
        for name in self.cleaned_data.get('tag_names', '').split(','):
            name = name.strip()
            if name:
                tag, _ = Tag.objects.get_or_create(
                    name=name,
                    defaults={'slug': name.lower().replace(' ', '-')},
                )
                tags.append(tag)
        blueprint.tags.set(tags)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Поделитесь впечатлениями...'}),
        }
