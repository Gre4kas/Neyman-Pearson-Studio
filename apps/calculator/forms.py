from django import forms
from django.core.exceptions import ValidationError

class CalculatorForm(forms.Form):
    # Вибір стовпця (стану), який контролюється
    CONTROLLED_STATE_CHOICES = [
        ('0', '1-й стовпець (L1)'),
        ('1', '2-й стовпець (L2)'),
    ]

    controlled_state = forms.ChoiceField(
        choices=CONTROLLED_STATE_CHOICES,
        label="Який стан контролюється?",
        initial='1',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    l_star = forms.FloatField(
        label="Граничне значення (L*)",
        initial=3.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
    )

    matrix_input = forms.CharField(
        label="Матриця втрат (кожен рядок - це стратегія)",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 6,
            "placeholder": "0, 4\n5, 1\n6, 3\n3, 2"
        }),
        help_text="Введіть числа через кому. Максимум 2 стовпці. Формат: L1, L2"
    )

    def clean_matrix_input(self):
        data = self.cleaned_data['matrix_input']
        lines = [line.strip() for line in data.strip().splitlines() if line.strip()]
        matrix = []
        
        if not lines:
            raise ValidationError("Матриця не може бути порожньою.")

        for idx, line in enumerate(lines):
            try:
                # Заміна крапок/ком для гнучкості
                parts = [float(x.strip()) for x in line.replace(';', ',').split(',')]
            except ValueError:
                raise ValidationError(f"Рядок {idx + 1} містить некоректні числа.")

            if len(parts) != 2:
                raise ValidationError(f"Рядок {idx + 1} має містити рівно 2 числа (2 стовпці).")
            
            matrix.append(parts)
        
        return matrix