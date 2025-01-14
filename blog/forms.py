from django import forms
from django.conf import settings
from django.core.mail import send_mail

from .models import Comment, Instruction

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment here...', 'id': 'comment-content'}),
        }
        labels = {
            'content': 'Your Comment',
        }

class InstructionForm(forms.ModelForm):
    class Meta:
        model = Instruction
        fields = ['step_number', 'text', 'image']

class RecipeRatingForm(forms.Form):
    rating = forms.IntegerField(min_value=0, max_value=5)

# blog/forms.py
from django import forms
from .models import Recipe, Instruction

class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['instructions'].queryset = Instruction.objects.filter(recipe=self.instance)
        else:
            self.fields['instructions'].queryset = Instruction.objects.none()


# blog/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    email_confirm = forms.EmailField(required=True, label="Confirm Email")

    class Meta:
        model = User
        fields = ['username', 'email', 'email_confirm', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Send the confirmation email (which will be printed to the console)
        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        subject = "Welcome to the Cooking Blog!"
        message = f"Hello {user.username},\n\nYou were successfully registered at the Cooking Blog with this email address: {user.email}.\n\nThank you for joining!"

        # This email will be displayed in the console due to the console backend
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Sender email address
            [user.email],  # Receiver email address (but this won't be actually used)
            fail_silently=False,
        )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        email_confirm = cleaned_data.get('email_confirm')

        if email and email != email_confirm:
            self.add_error('email_confirm', "Email addresses must match.")