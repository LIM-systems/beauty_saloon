from inwork import models as md
from datetime import timedelta
from django import forms
from django.core.exceptions import ValidationError

class VisitJournalForm(forms.ModelForm):
    class Meta:
        model = md.VisitJournal
        fields = '__all__'

    def clean(self):
        # проверка правильности вводимого значения
        cleaned_data = super().clean()
        math_action = cleaned_data.get('math_action')
        math_value = cleaned_data.get('math_value')
        visit_service = cleaned_data.get('visit_service')
        date = cleaned_data.get('date')
        
        if math_value:
            if math_value % 15 != 0:
                self.add_error('math_value', 'Значение должно быть кратным 15')
                return cleaned_data

            if math_action == 'minus':
                difference = visit_service.duration - math_value
                if difference <= 0:
                    self.add_error('math_value', 'Длительность услуги не может быть равна нулю.')
            else:
                new_time = date + timedelta(minutes=visit_service.duration) + timedelta(minutes=math_value)
                try:
                    visit = md.VisitJournal.objects.filter(
                            date__date=date.date(),
                            date__gt=date,  
                            visit_master=cleaned_data.get('visit_master'), 
                            cancel=False,
                            finish=False
                        ).order_by('date').first()
                    
                    if visit and new_time > visit.date:
                        self.add_error('math_value', 'Добавление времени приведет к конфликту с последующим визитом.')
                except md.VisitJournal.DoesNotExist:
                    pass

        return cleaned_data