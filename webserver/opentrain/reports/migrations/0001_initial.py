# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RawReport'
        db.create_table(u'reports_rawreport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'reports', ['RawReport'])


    def backwards(self, orm):
        # Deleting model 'RawReport'
        db.delete_table(u'reports_rawreport')


    models = {
        u'reports.rawreport': {
            'Meta': {'object_name': 'RawReport'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['reports']