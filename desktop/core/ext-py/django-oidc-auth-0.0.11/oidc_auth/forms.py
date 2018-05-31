from django import forms


class OpenIDConnectForm(forms.Form):
    issuer = forms.CharField(max_length=200,
            widget=forms.TextInput(attrs={'class': 'required openid'}))
