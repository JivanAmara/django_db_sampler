# coding=utf-8
""" @brief 
    @author jivan
    @since May 31, 2012
"""
from __future__ import unicode_literals, print_function, division
from db_sampler.models import Class1, Class2, Class3, BM2M1, BM2M2, TM2M1, TM2M2, \
    ThroughTable

# --- Set up objects for testing dependency analysis
o3 = Class3()
o3.save()
o2 = Class2(dep2=o3)
o2.save()
o1 = Class1(dep1=o2)
o1.save()

# --- Set up objects for testing basic many-to-many children analysis
# bm_1a will be related to zero objects
bm_1a = BM2M1(id=1)
# bm_1b will be related to bm_2a
bm_1b = BM2M1(id=2)
# bm_1c will be related to bm_2a and bm_2b
bm_1c = BM2M1(id=3)
# bm_1d will be related to bm_2a, bm_2b, and bm_2c
bm_1d = BM2M1(id=4)
bm1s = [bm_1a, bm_1b, bm_1c, bm_1d]

bm_2a = BM2M2(id=1)
bm_2b = BM2M2(id=2)
bm_2c = BM2M2(id=3)
bm2s = [bm_2a, bm_2b, bm_2c]

for bm2 in bm2s:
    bm2.save()

for i, bm1 in enumerate(bm1s):
    bm1.save()

    for bm2 in bm2s[:i]:
        bm1.m2m.add(bm2)

# --- Set up objects for testing m2m relationship with a 'through' model.
tm_1a = TM2M1(id=1)
tm_1a.save()
tm_2a = TM2M2(id=1)
tm_2a.save()
tm_2b = TM2M2(id=2)
tm_2b.save()
tm_2c = TM2M2(id=3)
tm_2c.save()

tt1 = ThroughTable(m2m1=tm_1a, m2m2=tm_2a)
tt1.save()
tt2 = ThroughTable(m2m1=tm_1a, m2m2=tm_2b)
tt2.save()
tt3 = ThroughTable(m2m1=tm_1a, m2m2=tm_2c)
tt3.save()
