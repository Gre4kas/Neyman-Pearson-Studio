from django import forms

DISTRIBUTION_CHOICES = [
    ('norm', 'Normal'),
    ('uniform', 'Uniform'),
    ('expon', 'Exponential'),
]

class CalculatorForm(forms.Form):
    alpha = forms.FloatField(
        label="Уровень значимости (α)", 
        min_value=0.0, 
        max_value=1.0, 
        initial=0.05,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    
    # H0 Hypothesis
    h0_dist = forms.ChoiceField(choices=DISTRIBUTION_CHOICES, label="H₀ Распределение")
    h0_param1 = forms.FloatField(label="H₀ Параметр 1 (loc/μ)", initial=0)
    h0_param2 = forms.FloatField(label="H₀ Параметр 2 (scale/σ)", initial=1)

    # H1 Hypothesis
    h1_dist = forms.ChoiceField(choices=DISTRIBUTION_CHOICES, label="H₁ Распределение")
    h1_param1 = forms.FloatField(label="H₁ Параметр 1 (loc/μ)", initial=1)
    h1_param2 = forms.FloatField(label="H₁ Параметр 2 (scale/σ)", initial=1)