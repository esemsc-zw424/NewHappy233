from django import forms
class CategoriesForm(forms.ModelForm):
     class Meta: model =  Categories = ['name','user']
