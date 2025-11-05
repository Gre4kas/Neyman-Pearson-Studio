from django import forms

DISTRIBUTION_CHOICES = [
    ('norm', 'Normal'),
    ('uniform', 'Uniform'),
    ('expon', 'Exponential'),
]

class CalculatorForm(forms.Form):
    alpha = forms.FloatField(
        label="Рівень значимості (α)", 
        min_value=0.0, 
        max_value=1.0, 
        initial=0.05,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    
    # H0 Hypothesis
    h0_dist = forms.ChoiceField(choices=DISTRIBUTION_CHOICES, label="H₀ Розподіл")
    h0_param1 = forms.FloatField(label="H₀ Параметр 1 (loc/μ)", initial=0)
    h0_param2 = forms.FloatField(
        label="H₀ Параметр 2 (scale/σ)", initial=1, min_value=0.0000001,
        error_messages={'min_value': 'Параметр scale/σ має бути > 0'}
    )

    # H1 Hypothesis
    h1_dist = forms.ChoiceField(choices=DISTRIBUTION_CHOICES, label="H₁ Розподіл")
    h1_param1 = forms.FloatField(label="H₁ Параметр 1 (loc/μ)", initial=1)
    h1_param2 = forms.FloatField(
        label="H₁ Параметр 2 (scale/σ)", initial=1, min_value=0.0000001,
        error_messages={'min_value': 'Параметр scale/σ має бути > 0'}
    )

    def clean(self):
        cleaned = super().clean()
        for scale_field in ('h0_param2', 'h1_param2'):
            val = cleaned.get(scale_field)
            if val is not None and val <= 0:
                self.add_error(scale_field, 'Параметр scale/σ має бути > 0')
        return cleaned