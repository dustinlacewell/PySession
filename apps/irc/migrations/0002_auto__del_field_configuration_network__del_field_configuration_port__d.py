# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Configuration.network'
        db.delete_column('irc_configuration', 'network')

        # Deleting field 'Configuration.port'
        db.delete_column('irc_configuration', 'port')

        # Deleting field 'Configuration.password'
        db.delete_column('irc_configuration', 'password')

        # Deleting field 'Configuration.nickname'
        db.delete_column('irc_configuration', 'nickname')


    def backwards(self, orm):
        
        # Adding field 'Configuration.network'
        db.add_column('irc_configuration', 'network', self.gf('django.db.models.fields.CharField')(default='irc.freenode.net', max_length=128), keep_default=False)

        # Adding field 'Configuration.port'
        db.add_column('irc_configuration', 'port', self.gf('django.db.models.fields.PositiveIntegerField')(default=6667), keep_default=False)

        # Adding field 'Configuration.password'
        db.add_column('irc_configuration', 'password', self.gf('django.db.models.fields.CharField')(default=datetime.date(2011, 2, 16), max_length=32), keep_default=False)

        # Adding field 'Configuration.nickname'
        db.add_column('irc_configuration', 'nickname', self.gf('django.db.models.fields.CharField')(default='NA', max_length=16), keep_default=False)


    models = {
        'irc.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'channel': ('django.db.models.fields.CharField', [], {'default': "'#pysession'", 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['irc']
