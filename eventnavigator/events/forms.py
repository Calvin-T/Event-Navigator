from django import forms

class CommentForm(forms.Form):
    #parent_Id = forms.CharField(widiget=forms.HiddenInput, required= False)
    content = forms.CharField(widget=forms.Textarea)
