from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from usuarios.models import Usuario

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Documento',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su documento de identidad',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )

    def clean_username(self):
        documento = self.cleaned_data.get('username')
        if documento:
            try:
                Usuario.objects.get(documento=documento)
            except Usuario.DoesNotExist:
                raise forms.ValidationError('No existe un usuario con este documento')
        return documento

class CustomRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['documento', 'nombres', 'apellidos', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Personalizar mensajes de ayuda
        self.fields['password1'].help_text = 'La contraseña debe tener al menos 8 caracteres'
        self.fields['password2'].help_text = 'Repite la contraseña'
        
        # Agregar validación para el campo documento
        self.fields['documento'].widget.attrs.update({
            'maxlength': '10',
            'pattern': '\d{10}',
            'title': 'El documento debe tener exactamente 10 dígitos numéricos'
        })
    
    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if not documento or not documento.isdigit() or len(documento) != 10:
            raise forms.ValidationError('El documento debe tener exactamente 10 dígitos numéricos.')
        return documento
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.documento  # Usar el documento como username
        user.rol = 'instructor'  # Asignar rol instructor por defecto
        if commit:
            user.save()
        return user
