from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
        
        # Update labels to Russian
        self.fields['username'].label = 'Имя пользователя'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        
        # Remove help text for cleaner look
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
