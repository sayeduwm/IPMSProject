from django import forms
from django.utils.translation import ugettext_lazy as _

from ipms.models import RequestTest
from ipms.models import SpotCheck 
from ipms.models import LeaveSpot 

LABEL_CHOICES = (
    ('django', 'Django'),
    ('python', 'Python'),
)

class EntryForm(forms.ModelForm):
    
    
    
    class Meta:
        model = RequestTest       
        fields = '__all__'#('Yourstatus', 'Lat', 'Lon', 'Destination', 'Date')
        exclude = ['pdate','parkno','pprice','pid','pprice','pcost']
        labels = {'yourstatus': _('Your Status')  }     
         

class EntryFormsStaff(forms.ModelForm):
    
    
    
    class Meta:
        model =SpotCheck      
        fields = '__all__'#('Yourstatus', 'Lat', 'Lon', 'Destination', 'Date')
        exclude = ['id']
        labels = {'yourstatus': _('Your Status')  } 
        
        
CHARACTER_ENCODINGS = [("ascii", "ASCII"),("latin1", "Latin-1"), ("utf8", "UTF-8")]

class ImportShapefileForm(forms.Form):
    import_file = forms.FileField(label="Select a Zipped Shapefile")
    character_encoding = forms.ChoiceField(choices=CHARACTER_ENCODINGS, initial="utf8")
    #name=forms.CharField()

class LeaveSpotForm(forms.ModelForm):
    
    
    
    class Meta:
        model = LeaveSpot       
        fields = '__all__'#('Yourstatus', 'Lat', 'Lon', 'Destination', 'Date')
        exclude = ['pdate','parkno','pprice','pid','pprice','pcost']
        labels = {'yourstatus': _('Your Status')  } 

