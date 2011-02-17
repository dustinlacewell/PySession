# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Snippit'
        db.create_table('snippits_snippit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('code', self.gf('django.db.models.fields.TextField')()),
            ('result', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('snippits', ['Snippit'])


    def backwards(self, orm):
        
        # Deleting model 'Snippit'
        db.delete_table('snippits_snippit')


    models = {
        'snippits.snippit': {
            'Meta': {'object_name': 'Snippit'},
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['snippits']
