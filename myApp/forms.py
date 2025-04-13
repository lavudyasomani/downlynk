from django import forms
from .models import MediaFile

class MediaDownloadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['url']
        widgets = {
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter media URL (image, video, audio, etc.)'
            })
        }


class VideoDownloadForm(forms.Form):
    url = forms.URLField(label='Enter Video URL', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Video URL . . .'}))


class VideoURLForm(forms.Form):
    url = forms.URLField(label="Video URL", widget=forms.URLInput(attrs={
        "class": "form-control", "placeholder": "Enter Video URL..."
    }))


from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
