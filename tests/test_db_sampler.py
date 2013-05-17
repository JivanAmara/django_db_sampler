# coding=utf-8
""" @brief 
    @author jivan
    @since May 31, 2012
"""
from __future__ import unicode_literals, print_function, division
from db_sampler.db_sampler_script import identify_dependencies, \
    identify_simple_children, identify_basic_m2m_children, \
    identify_through_m2m_children, sample_object
from db_sampler.models import Class1, Class3, Class2, BM2M1, BM2M2, TM2M1, TM2M2, \
    ThroughTable
from django.core.management import call_command
from django.test import TestCase

class DBSamplerTests(TestCase):
    """ @brief Tests for the db_sampler functions.
    """
    fixtures = ['db_sampler_fixture.json']
    
    # Fixture maker database alias (This needs to match the definition in settings.py)
    fm_db_alias = 'fixture_maker'

    def setUp(self):
        self.b1a = BM2M1.objects.get(id=1)
        self.b1b = BM2M1.objects.get(id=2)
        self.b1c = BM2M1.objects.get(id=3)
        self.b1d = BM2M1.objects.get(id=4)

        self.b2a = BM2M2.objects.get(id=1)
        self.b2b = BM2M2.objects.get(id=2)
        self.b2c = BM2M2.objects.get(id=3)

        # Dictionary keying BM2M1 objects to a list of the BM2M2 objects they are
        #    related to with a ManyToManyRel.
        self.basics = {
            self.b1a: [],
            self.b1b: [self.b2a],
            self.b1c: [self.b2a, self.b2b],
            self.b1d: [self.b2a, self.b2b, self.b2c]
        }
    def test_identify_dependencies(self):
        """ @brief Checks that identify_dependencies() does its job properly.
        """
        obj1 = Class1.objects.get(id=1)
        deps = identify_dependencies(obj1)
        self.failUnlessEqual(type(deps[0]), Class3)
        self.failUnlessEqual(type(deps[1]), Class2)
        self.failUnlessEqual(len(deps), 2)

    def test_identify_simple_children(self):
        """ @brief Checks that identify_simple_children() does its job properly.
        """
        obj3 = Class3.objects.get(id=1)
        obj2 = Class2.objects.get(id=1)
        obj1 = Class1.objects.get(id=1)

        # Default depth is 1
        children = identify_simple_children(obj3)
        # Then comes the child
        self.failUnlessEqual(children[0], obj2)
        self.failUnlessEqual(len(children), 1)
        
        # Check with depth = 2
        children = identify_simple_children(obj3, depth=2)
        self.failUnlessEqual(children[0], obj2)
        self.failUnlessEqual(children[1], obj1)

        self.failUnlessEqual(len(children), 2)
        
    def test_identify_basic_m2m_children(self):
        """ @brief Checks that identify_basic_m2m_children() does its
                job properly.
        """
        # Basic many-to-many children of BM2M1 objects
        for obj, expected_children in self.basics.items():
            fields_with_children = identify_basic_m2m_children(obj)
            children = fields_with_children['m2m']
            self.failUnlessEqual(children, expected_children)
        
        # Ensure that m2m relationships with a custom through table are ignored.
        t1a = TM2M1.objects.get(id=1)
        mcs = identify_basic_m2m_children(t1a)
        self.failUnlessEqual(mcs, {})

    def test_identify_through_m2m_children(self):
        """ @brief Checks that identify_through_m2m_children() does its
                job properly.
        """
        # One side of the m2m relationship
        t1a = TM2M1.objects.get(id=1)
        
        # The other side of the m2m relationship
        t2a = TM2M2.objects.get(id=1)
        t2b = TM2M2.objects.get(id=2)
        t2c = TM2M2.objects.get(id=3)
        
        # The through-table entries
        tt1 = ThroughTable.objects.get(id=1)
        tt2 = ThroughTable.objects.get(id=2)
        tt3 = ThroughTable.objects.get(id=3)
        
        # children, connection objects
        children, connections = identify_through_m2m_children(t1a)
        self.failUnlessEqual(children, [t2a, t2b, t2c])
        self.failUnlessEqual(connections, [tt1, tt2, tt3])

        # Ensure that managed m2m relationships are ignored.
        b = BM2M1.objects.get(id=4)
        children, connections = identify_through_m2m_children(b)
        self.failUnlessEqual(children, [])
        self.failUnlessEqual(connections, [])

class SampleObjectTests(TestCase):
    """ @brief Tests for sample_object()
    """
    fixtures = ['db_sampler_fixture.json']
    
    def empty_fixture_db(self):
        call_command('flush', database='fixture_maker', interactive=False, verbosity=0)
        
    def test_single_object_no_dependencies(self):
        self.empty_fixture_db()
        
        c1 = Class3.objects.using('fixture_maker').count()
        self.failUnlessEqual(c1, 0)
        
        obj = Class3.objects.get(id=1)
        sample_object(obj, db_alias='fixture_maker')
        c2 = Class3.objects.using('fixture_maker').count()
        self.failUnlessEqual(c2, 1)
        
        # By default, sample_object should collect direct children.
        c3 = Class2.objects.using('fixture_maker').count()
        self.failUnlessEqual(c3, 1)
    
    def test_single_object_1_deep_dependency(self):
        self.empty_fixture_db()
        
        c = Class2.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 0)
        
        obj = Class2.objects.get(id=1)
        sample_object(obj, db_alias='fixture_maker')
        c = Class2.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 1)
        
        # A Class3 object should be saved as a dependency
        c = Class3.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 1)
        
        # By default, sample_object should collect direct children.
        c = Class1.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 1)

    def test_single_object_2_deep_dependency(self):
        self.empty_fixture_db()
        
        c = Class1.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 0)
        
        obj = Class1.objects.get(id=1)
        sample_object(obj, db_alias='fixture_maker')
        c = Class1.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 1)
        
        # A Class2 object should be saved as a dependency
        c = Class3.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 1)
        
        # A Class3 object should be saved as a dependency of the Class2 dependency
        c = Class3.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 1)

    def test_simple_m2m_children(self):
        self.empty_fixture_db()
        
        c = BM2M1.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 0)
        c = BM2M2.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 0)

        # Object with three m2m children
        obj = BM2M1.objects.get(id=4)
        sample_object(obj, db_alias='fixture_maker')
        c = BM2M1.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 1)
        c = BM2M2.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 3)

        # Ensure the fixture database version is connected to its children
        obj = BM2M1.objects.using('fixture_maker').get()
        c = obj.m2m.count()
        self.failUnlessEqual(c, 3)

    def test_through_m2m_children(self):
        self.empty_fixture_db()
        
        c = TM2M1.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 0)
        c = TM2M2.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 0)
        c = ThroughTable.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 0)
        
        # An object with three m2m children using a custom through model.
        obj = TM2M1.objects.get(id=1)
        sample_object(obj)
        c = TM2M1.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 1)
        c = TM2M2.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 3)
        c = ThroughTable.objects.using('fixture_maker').count()
        self.failUnlessEqual(c, 3)
        