# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AnalysisMarker'
        db.create_table(u'analysis_analysismarker', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('lat', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('lon', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'analysis', ['AnalysisMarker'])

        # Adding model 'RealTimeStop'
        db.create_table(u'analysis_realtimestop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tracker_id', self.gf('django.db.models.fields.CharField')(max_length=40, db_index=True)),
            ('trip', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gtfs.Trip'])),
            ('stop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gtfs.Stop'])),
            ('arrival_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('departure_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'analysis', ['RealTimeStop'])

        # Adding unique constraint on 'RealTimeStop', fields ['tracker_id', 'trip', 'stop']
        db.create_unique(u'analysis_realtimestop', ['tracker_id', 'trip_id', 'stop_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'RealTimeStop', fields ['tracker_id', 'trip', 'stop']
        db.delete_unique(u'analysis_realtimestop', ['tracker_id', 'trip_id', 'stop_id'])

        # Deleting model 'AnalysisMarker'
        db.delete_table(u'analysis_analysismarker')

        # Deleting model 'RealTimeStop'
        db.delete_table(u'analysis_realtimestop')


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
        u'analysis.realtimestop': {
            'Meta': {'unique_together': "(('tracker_id', 'trip', 'stop'),)", 'object_name': 'RealTimeStop'},
            'arrival_time': ('django.db.models.fields.DateTimeField', [], {}),
            'departure_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gtfs.Stop']"}),
            'tracker_id': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'}),
            'trip': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gtfs.Trip']"})
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
        },
        u'gtfs.agency': {
            'Meta': {'object_name': 'Agency'},
            'agency_id': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '255', 'primary_key': 'True'}),
            'agency_lang': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'agency_name': ('django.db.models.fields.TextField', [], {}),
            'agency_timezone': ('django.db.models.fields.TextField', [], {}),
            'agency_url': ('django.db.models.fields.TextField', [], {})
        },
        u'gtfs.route': {
            'Meta': {'object_name': 'Route'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gtfs.Agency']", 'null': 'True', 'blank': 'True'}),
            'route_color': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'route_desc': ('django.db.models.fields.TextField', [], {}),
            'route_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'route_long_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'route_short_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'route_text_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'route_type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'gtfs.service': {
            'Meta': {'object_name': 'Service'},
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'friday': ('django.db.models.fields.BooleanField', [], {}),
            'monday': ('django.db.models.fields.BooleanField', [], {}),
            'saturday': ('django.db.models.fields.BooleanField', [], {}),
            'service_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'sunday': ('django.db.models.fields.BooleanField', [], {}),
            'thursday': ('django.db.models.fields.BooleanField', [], {}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {})
        },
        u'gtfs.stop': {
            'Meta': {'object_name': 'Stop'},
            'location_type': ('django.db.models.fields.IntegerField', [], {}),
            'stop_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'stop_lat': ('django.db.models.fields.FloatField', [], {}),
            'stop_lon': ('django.db.models.fields.FloatField', [], {}),
            'stop_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'stop_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'gtfs.trip': {
            'Meta': {'object_name': 'Trip'},
            'direction_id': ('django.db.models.fields.IntegerField', [], {}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gtfs.Route']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gtfs.Service']"}),
            'shape_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'trip_headsign': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'trip_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'wheelchair_accessible': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['analysis']