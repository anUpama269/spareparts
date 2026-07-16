from django import forms
from .models import CustomUser, AccessPermission, Role

class UserForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    access_permissions = forms.ModelMultipleChoiceField(
        queryset=AccessPermission.objects.none(), required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['access_permissions'].queryset = AccessPermission.objects.order_by('module', 'name')
        if not self.instance.pk:
            self.fields['password'].required = True

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'phone', 'password', 'is_active', 'access_permissions']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user


class SignupForm(UserForm):
    class Meta(UserForm.Meta):
        fields = ['username', 'email', 'phone', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('role', None)
        self.fields.pop('access_permissions', None)
        self.fields.pop('is_active', None)


class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=AccessPermission.objects.none(), required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = AccessPermission.objects.order_by('module', 'name')


class AccessPermissionForm(forms.ModelForm):
    class Meta:
        model = AccessPermission
        fields = ['name', 'module', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'module': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
