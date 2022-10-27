from django import forms
from .models import DirectMessage


class DirectMessageForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={
        "class": "test-class-for-styling",
        "rows": 3,
        "pkaceholder": "Type your message here....",
        "style": "width: 100%; background-color: pink;"
    }))
    class Meta:
        model = DirectMessage
        fields = ['body']