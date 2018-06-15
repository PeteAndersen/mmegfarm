from django import forms

from bestiary import parse


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def parse_creatures(self):
        return parse.creatures(self.cleaned_data.get('file'))

