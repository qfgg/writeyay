from django import forms

class EssayForm(forms.Form):
    topic = forms.CharField(widget=forms.Textarea(attrs={
        'id': 'topic-textarea',
        'rows': 1,
    }))
    essay = forms.CharField(widget=forms.Textarea(attrs={
        'id': 'essay-textarea',
        'rows': 5,
    }))
