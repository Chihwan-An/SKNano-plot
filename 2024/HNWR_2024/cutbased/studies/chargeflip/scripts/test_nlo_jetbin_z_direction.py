import unittest
import numpy as np
from nlo_jetbin_z_direction import accumulate, moments
from jetbin_lepton_shapes import norm, estimate


class NLODirectionTest(unittest.TestCase):
    def test_signed_weight_moments(self):
        x=np.array([1.,2.,4.]); w=np.array([2.,-1.,3.])
        m=moments(x,w)
        np.testing.assert_allclose(m,[4,14,12,42,152])
        got=estimate(m)
        self.assertAlmostEqual(got['value'],3)
        self.assertAlmostEqual(got['error']**2,26/16)

    def test_signed_histogram_and_normalization(self):
        d=dict(l1_pt=np.array([100.,100.,100.]),l2_pt=np.array([80.,80.,80.]),
               l1_eta=np.zeros(3),l2_eta=np.zeros(3),
               l1_phi=np.zeros(3),l2_phi=np.full(3,2.))
        q=np.sqrt(100**2+80**2+2*100*80*np.cos(2.))
        mass=np.sqrt(2*100*80*(1-np.cos(2.)))
        d.update(pt_l1l2=np.full(3,q),m_l1l2=np.full(3,mass),
                 weight=np.array([2.,-1.,3.]),nJet=np.ones(3),channel=np.full(3,11))
        h,v,r=accumulate(d)['EE/inclusive/all_zpt']
        self.assertEqual(h['eta'][1].sum(),4)
        self.assertEqual(v['eta'][1].sum(),14)
        self.assertEqual(r['1j']['negative_entries'],1)
        self.assertEqual(r['1j']['mc_entries'],3)
        shape,var=norm(h['eta'][1],v['eta'][1])
        self.assertAlmostEqual(shape.sum(),1)
        self.assertTrue(np.all(var>=0))


if __name__=='__main__': unittest.main()
