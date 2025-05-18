from django import forms
from .models import City, Dish, Reservation

class DishFilterForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False, label="City")
    type = forms.ChoiceField(choices=[('', 'All')] + Dish.TYPE_CHOICES, required=False, label="Dish Type")
    is_vegetarian = forms.BooleanField(required=False, label="Vegetarian Only")
    is_vegan = forms.BooleanField(required=False, label="Vegan Only")
    price_range = forms.MultipleChoiceField(
        choices=Dish.price_range.field.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Price Range"
    )
    bad_for_cholesterol = forms.BooleanField(
        required=False,
        label="I have cholesterol issues",
        widget=forms.CheckboxInput(attrs={'class': 'health-checkbox'})
    )
    bad_for_sugar = forms.BooleanField(
        required=False,
        label="I have diabetes",
        widget=forms.CheckboxInput(attrs={'class': 'health-checkbox'})
    )
    bad_for_lactose = forms.BooleanField(
        required=False,
        label="I am lactose intolerant",
        widget=forms.CheckboxInput(attrs={'class': 'health-checkbox'})
    )

class CurrencyConverterForm(forms.Form):
    CURRENCY_CHOICES = [
        ('USD', '🇺🇸 Dollar (USD)'),
        ('EUR', '🇪🇺 Euro (EUR)'),
        ('GBP', '🇬🇧 Livre Sterling (GBP)'),
        ('CAD', '🇨🇦 Dollar Canadien (CAD)'),
        ('AED', '🇦🇪 Dirham Émirati (AED)'),
        ('CHF', '🇨🇭 Franc Suisse (CHF)'),
        ('JPY', '🇯🇵 Yen Japonais (JPY)'),
        ('CNY', '🇨🇳 Yuan Chinois (CNY)'),
        ('SAR', '🇸🇦 Riyal Saoudien (SAR)'),
    ]
    
    amount = forms.DecimalField(label='Montant')
    from_currency = forms.ChoiceField(choices=CURRENCY_CHOICES, label='Devise')

class ReservationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Choisissez une date pour votre réservation'
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text='Choisissez une heure pour votre réservation'
    )
    guests = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=2,
        help_text='Nombre de personnes (max 20)'
    )
    
    class Meta:
        model = Reservation
        fields = ['name', 'email', 'phone', 'date', 'time', 'guests', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Précisez vos demandes spéciales...'}),
        }
