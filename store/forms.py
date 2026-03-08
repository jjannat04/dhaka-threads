from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class DhakaThreadsSignupForm(UserCreationForm):

    email = forms.EmailField(required=True, help_text="Required. A valid email address is needed for activation.")

    class Meta(UserCreationForm.Meta):
        model = User
        
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user