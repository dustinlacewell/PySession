# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Snippit.highlight'
        db.add_column('snippits_snippit', 'highlight', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Snippit.highlight'
        db.delete_column('snippits_snippit', 'highlight')


    models = {
        'snippits.snippit': {
            'Meta': {'object_name': 'Snippit'},
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {}),
            'highlight': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['snippits']
