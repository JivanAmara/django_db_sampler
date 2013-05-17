# coding=utf-8
""" @brief 
    @author jivan
    @since May 31, 2012
"""
from __future__ import unicode_literals, print_function, division
from django.db import models

class Class3 (models.Model):
    # This attribute isn't really used...the model just needs to have one.
    nodep = models.IntegerField(null=True, blank=True)

class Class2(models.Model):
    # Dependency on Class3
    dep2 = models.ForeignKey(Class3)

class Class1(models.Model):
    # Dependency on Class2
    dep1 = models.ForeignKey(Class2)


# Basic Many-to-Many Relationships are those managed by Django.  The
#    details of the mapping table don't need to be dealt with.
class BM2M1(models.Model):
    # Many-to-many relationship between BM2M2 <-> BM2M1
    m2m = models.ManyToManyField('BM2M2')

class BM2M2(models.Model):
    # This attribute isn't really used...the model just needs to have one.
    attr = models.IntegerField(null=True, blank=True)

# Through Many-to-Many relationships are those where a 'through' parameter is
#   given to the ManyToManyField, and a third model is used as the mapping table.
#   In this scenario, Django doesn't manage the mapping table and the relationships
#   must be managed manually through inserts and deletes in this mapping table.
class TM2M1(models.Model):
    # This attribute isn't really used...the model just needs to have one.
    m2m = models.ManyToManyField('TM2M2', through='ThroughTable')
    
class TM2M2(models.Model):
    # This attribute isn't really used...the model just needs to have one.
    attr = models.IntegerField(null=True, blank=True)

class ThroughTable(models.Model):
    m2m1 = models.ForeignKey(TM2M1)
    m2m2 = models.ForeignKey(TM2M2)
    
    # Through tables are used to add information to a relationship
    extra_info = models.IntegerField(null=True, blank=True)
