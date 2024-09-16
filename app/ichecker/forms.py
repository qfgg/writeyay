from django import forms

class EssayForm(forms.Form):
    topic = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'topic-textarea',
            'rows': 1,
        }),
        error_messages={
            'required': 'Please enter a topic',
        }
    )
    essay = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'essay-textarea',
            'rows': 5,
        }),
        error_messages={
            'required': 'Please enter an IELTS essay for analysis',
        }
    )
    word_count = forms.IntegerField(
        widget=forms.HiddenInput(attrs={
            'id': 'word-count-input',
        }),
        required=False
    )
