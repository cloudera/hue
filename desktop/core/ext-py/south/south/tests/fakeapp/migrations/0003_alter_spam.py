from south.db import db
from django.db import models

class Migration:
    
    def forwards(self):
        
        db.alter_column("southtest_spam", 'name', models.CharField(max_length=255, null=True))
    
    def backwards(self):
        
        db.alter_column("southtest_spam", 'name', models.CharField(max_length=255))

    models = {
        "fakeapp.bug135": {
            'date':  ('models.DateTimeField', [], {'default': 'datetime.datetime(2009, 5, 6, 15, 33, 15, 780013)'}),
        }
    }
