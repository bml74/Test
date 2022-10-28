from django import forms
from .models import DirectMessage


class DirectMessageForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={
        "class": "test-class-for-styling",
        "rows": 2,
        "pkaceholder": "Type your message here....",
    }))
    class Meta:
        model = DirectMessage
        fields = ['body']