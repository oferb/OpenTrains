# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TrainData'
        db.create_table(u'traindata_traindata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('train_num', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('exp_arrival', self.gf('django.db.models.fields.IntegerField')()),
            ('actual_arrival', self.gf('django.db.models.fields.IntegerField')()),
            ('exp_departure', self.gf('django.db.models.fields.IntegerField')()),
            ('actual_departure', self.gf('django.db.models.fields.IntegerField')()),
            ('raw_stop_id', self.gf('django.db.models.fields.IntegerField')()),
            ('raw_stop_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('stop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gtfs.Stop'], null=True, blank=True)),
            ('file', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('line', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'traindata', ['TrainData'])


    def backwards(self, orm):
        # Deleting model 'TrainData'
        db.delete_table(u'traindata_traindata')


    models = {
        u'gtfs.stop': {
            'Meta': {'object_name': 'Stop'},
            'location_type': ('django.db.models.fields.IntegerField', [], {}),
            'stop_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'stop_lat': ('django.db.models.fields.FloatField', [], {}),
            'stop_lon': ('django.db.models.fields.FloatField', [], {}),
            'stop_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'stop_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'traindata.traindata': {
            'Meta': {'object_name': 'TrainData'},
            'actual_arrival': ('django.db.models.fields.IntegerField', [], {}),
            'actual_departure': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'exp_arrival': ('django.db.models.fields.IntegerField', [], {}),
            'exp_departure': ('django.db.models.fields.IntegerField', [], {}),
            'file': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.IntegerField', [], {}),
            'raw_stop_id': ('django.db.models.fields.IntegerField', [], {}),
            'raw_stop_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gtfs.Stop']", 'null': 'True', 'blank': 'True'}),
            'train_num': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['traindata']