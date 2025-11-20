from django import forms

CONTROLLED_STATE_CHOICES = [
    (0, 'L1 контролюється'),
    (1, 'L2 контролюється'),
]

class MatrixCalculatorForm(forms.Form):
    controlled_state = forms.ChoiceField(
        choices=CONTROLLED_STATE_CHOICES, 
        label="Контрольований стан",
        widget=forms.RadioSelect,
        initial=0
    )
    L_star = forms.FloatField(label="Граничне значення L*", initial=4.2)

    strategies_input = forms.CharField(
        label="Матриця стратегій (L, J) через кому, кожна стратегія з нового рядка",
        widget=forms.Textarea(attrs={
            "rows": 6,
            "placeholder": "3.5,4.4\n8.2,6.4\n1.5,2.4\n0.4,8.5\n..."
        }),
        help_text="Введіть стратегії у форматі: L, J, по одному на рядок."
    )

    def clean_strategies_input(self):
        data = self.cleaned_data['strategies_input']
        lines = [line.strip() for line in data.strip().splitlines() if line.strip()]
        strategies = {}
        for idx, line in enumerate(lines):
            parts = line.split(',')
            if len(parts) != 2:
                raise forms.ValidationError(f"Стратегія в рядку {idx+1} має містити 2 числа через кому.")
            try:
                L = float(parts[0].strip())
                J = float(parts[1].strip())
            except ValueError:
                raise forms.ValidationError(f"Некоректне число в рядку {idx+1}.")
            strategies[f"a{idx+1}"] = (L, J)
        return strategies
    
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