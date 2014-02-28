# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Report'
        db.create_table(u'analysis_report', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('device_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'analysis', ['Report'])

        # Adding model 'LocationInfo'
        db.create_table(u'analysis_locationinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.OneToOneField')(related_name='my_loc', unique=True, to=orm['analysis.Report'])),
            ('accuracy', self.gf('django.db.models.fields.FloatField')()),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('lon', self.gf('django.db.models.fields.FloatField')()),
            ('provider', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'analysis', ['LocationInfo'])

        # Adding model 'SingleWifiReport'
        db.create_table(u'analysis_singlewifireport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wifi_set', to=orm['analysis.Report'])),
            ('SSID', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('frequency', self.gf('django.db.models.fields.FloatField')()),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('signal', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'analysis', ['SingleWifiReport'])

        # Adding model 'AnalysisMarker'
        db.create_table(u'analysis_analysismarker', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('lat', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('lon', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'analysis', ['AnalysisMarker'])


    def backwards(self, orm):
        # Deleting model 'Report'
        db.delete_table(u'analysis_report')

        # Deleting model 'LocationInfo'
        db.delete_table(u'analysis_locationinfo')

        # Deleting model 'SingleWifiReport'
        db.delete_table(u'analysis_singlewifireport')

        # Deleting model 'AnalysisMarker'
        db.delete_table(u'analysis_analysismarker')


    models = {
        u'analysis.analysismarker': {
            'Meta': {'object_name': 'AnalysisMarker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'analysis.locationinfo': {
            'Meta': {'object_name': 'LocationInfo'},
            'accuracy': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lon': ('django.db.models.fields.FloatField', [], {}),
            'provider': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'report': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'my_loc'", 'unique': 'True', 'to': u"orm['analysis.Report']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'analysis.report': {
            'Meta': {'object_name': 'Report'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'analysis.singlewifireport': {
            'Meta': {'object_name': 'SingleWifiReport'},
            'SSID': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'frequency': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wifi_set'", 'to': u"orm['analysis.Report']"}),
            'signal': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['analysis']