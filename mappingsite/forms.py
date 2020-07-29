from django import forms

formatchoices = (('pdf', 'pdf'),('jpeg', 'jpeg'), ('jpg', 'jpg'), ('png', 'png'), ('html', 'html'), ('all', 'all'))

class SelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        urlchoices = kwargs.pop('urlchoices')
        super(SelectionForm, self).__init__(*args, **kwargs)
        self.fields['urlchoice'] = forms.ChoiceField(choices=urlchoices, required=False)
        self.fields['formatchoice'] = forms.ChoiceField(choices=formatchoices, required=False)
        self.fields['depth'] = forms.ChoiceField(choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')), required=False)