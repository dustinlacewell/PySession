# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Configuration'
        db.create_table('irc_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.CharField')(default='irc.freenode.net', max_length=128)),
            ('port', self.gf('django.db.models.fields.PositiveIntegerField')(default=6667)),
            ('channel', self.gf('django.db.models.fields.CharField')(default='#pysession', max_length=32)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('irc', ['Configuration'])


    def backwards(self, orm):
        
        # Deleting model 'Configuration'
        db.delete_table('irc_configuration')


    models = {
        'irc.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'channel': ('django.db.models.fields.CharField', [], {'default': "'#pysession'", 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'default': "'irc.freenode.net'", 'max_length': '128'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '6667'})
        }
    }

    complete_apps = ['irc']
