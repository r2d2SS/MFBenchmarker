from django import forms

class MarginForm(forms.Form):
    new_margin = forms.IntegerField(label="Margin", max_value=100, min_value=0)