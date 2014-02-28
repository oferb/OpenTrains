# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Agency'
        db.create_table(u'gtfs_agency', (
            ('agency_id', self.gf('django.db.models.fields.IntegerField')(default=1, max_length=255, primary_key=True)),
            ('agency_name', self.gf('django.db.models.fields.TextField')()),
            ('agency_url', self.gf('django.db.models.fields.TextField')()),
            ('agency_timezone', self.gf('django.db.models.fields.TextField')()),
            ('agency_lang', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'gtfs', ['Agency'])

        # Adding model 'Route'
        db.create_table(u'gtfs_route', (
            ('route_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gtfs.Agency'], null=True, blank=True)),
            ('route_short_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('route_long_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('route_desc', self.gf('django.db.models.fields.TextField')()),
            ('route_type', self.gf('django.db.models.fields.IntegerField')()),
            ('route_color', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('route_text_color', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'gtfs', ['Route'])

        # Adding model 'Service'
        db.create_table(u'gtfs_service', (
            ('service_id', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('monday', self.gf('django.db.models.fields.BooleanField')()),
            ('tuesday', self.gf('django.db.models.fields.BooleanField')()),
            ('wednesday', self.gf('django.db.models.fields.BooleanField')()),
            ('thursday', self.gf('django.db.models.fields.BooleanField')()),
            ('friday', self.gf('django.db.models.fields.BooleanField')()),
            ('saturday', self.gf('django.db.models.fields.BooleanField')()),
            ('sunday', self.gf('django.db.models.fields.BooleanField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'gtfs', ['Service'])

        # Adding model 'Trip'
        db.create_table(u'gtfs_trip', (
            ('route', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gtfs.Route'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gtfs.Service'])),
            ('trip_id', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('direction_id', self.gf('django.db.models.fields.IntegerField')()),
            ('shape_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('wheelchair_accessible', self.gf('django.db.models.fields.IntegerField')()),
            ('trip_headsign', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'gtfs', ['Trip'])

        # Adding model 'Stop'
        db.create_table(u'gtfs_stop', (
            ('stop_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('stop_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('stop_lat', self.gf('django.db.models.fields.FloatField')()),
            ('stop_lon', self.gf('django.db.models.fields.FloatField')()),
            ('stop_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('location_type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'gtfs', ['Stop'])

        # Adding model 'StopTime'
        db.create_table(u'gtfs_stoptime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('trip', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gtfs.Trip'])),
            ('arrival_time', self.gf('django.db.models.fields.IntegerField')()),
            ('departure_time', self.gf('django.db.models.fields.IntegerField')()),
            ('stop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gtfs.Stop'])),
            ('stop_sequence', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'gtfs', ['StopTime'])

        # Adding model 'Shape'
        db.create_table(u'gtfs_shape', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shape_id', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('shape_pt_lat', self.gf('django.db.models.fields.FloatField')()),
            ('shape_pt_lon', self.gf('django.db.models.fields.FloatField')()),
            ('shape_pt_sequence', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'gtfs', ['Shape'])

        # Adding model 'ShapeJson'
        db.create_table(u'gtfs_shapejson', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shape_id', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('points', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'gtfs', ['ShapeJson'])


    def backwards(self, orm):
        # Deleting model 'Agency'
        db.delete_table(u'gtfs_agency')

        # Deleting model 'Route'
        db.delete_table(u'gtfs_route')

        # Deleting model 'Service'
        db.delete_table(u'gtfs_service')

        # Deleting model 'Trip'
        db.delete_table(u'gtfs_trip')

        # Deleting model 'Stop'
        db.delete_table(u'gtfs_stop')

        # Deleting model 'StopTime'
        db.delete_table(u'gtfs_stoptime')

        # Deleting model 'Shape'
        db.delete_table(u'gtfs_shape')

        # Deleting model 'ShapeJson'
        db.delete_table(u'gtfs_shapejson')


    models = {
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
        u'gtfs.shape': {
            'Meta': {'object_name': 'Shape'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shape_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'shape_pt_lat': ('django.db.models.fields.FloatField', [], {}),
            'shape_pt_lon': ('django.db.models.fields.FloatField', [], {}),
            'shape_pt_sequence': ('django.db.models.fields.IntegerField', [], {})
        },
        u'gtfs.shapejson': {
            'Meta': {'object_name': 'ShapeJson'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.TextField', [], {}),
            'shape_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
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
        u'gtfs.stoptime': {
            'Meta': {'object_name': 'StopTime'},
            'arrival_time': ('django.db.models.fields.IntegerField', [], {}),
            'departure_time': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stop': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gtfs.Stop']"}),
            'stop_sequence': ('django.db.models.fields.IntegerField', [], {}),
            'trip': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gtfs.Trip']"})
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

    complete_apps = ['gtfs']