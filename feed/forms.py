from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models

# Form model - using built-in UserCreationForm registration form
class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

# Uploading Files Form
class UploadFile(models.Model):
	title = models.CharField(max_length=255)
	file = models.FileField(upload_to='files')

class ModelFormWithFileField(ModelForm):
	class Meta:
		model = UploadFile
		fields = "__all__"

# Uploading Images Form
class UploadImage(models.Model):
	title = models.CharField(max_length=255)
	alt = models.CharField(max_length=255)
	file = models.ImageField(upload_to='images')

class ModelFormWithImageField(ModelForm):
	class Meta:
		model = UploadImage
		fields = "__all__"