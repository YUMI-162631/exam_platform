from django import forms
from .models import User

# UserRegistrationForm（ユーザー登録フォーム）
class UserRegistrationForm(forms.ModelForm):
    """ユーザー登録フォーム"""
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'パスワードを入力'
        })
    )
    password_confirm = forms.CharField(
        label='パスワード（確認）',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'パスワードを再入力'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ユーザー名を入力'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'メールアドレスを入力'
            }),
        }
        labels = {
            'username': 'ユーザー名',
            'email': 'メールアドレス',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('パスワードが一致しません。')
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に登録されています。')
        return email

# LoginForm（ログインフォーム）
class LoginForm(forms.Form):
    """ログインフォーム"""
    email = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'メールアドレスを入力'
        })
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'パスワードを入力'
        })
    )