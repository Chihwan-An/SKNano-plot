import unittest
import numpy as np
from jetbin_z_direction import reconstruct


class ZDirectionTest(unittest.TestCase):
    def pair(self,eta1,eta2,rotation=0.):
        p1=np.array([100.,120.,150.]); p2=np.array([80.,80.,130.])
        f1=np.array([.2,.5,-.7])+rotation; f2=np.array([2.,2.6,1.9])+rotation
        e1=np.full(3,eta1); e2=np.full(3,eta2)
        q=np.hypot(p1*np.cos(f1)+p2*np.cos(f2),p1*np.sin(f1)+p2*np.sin(f2))
        m=np.sqrt(2*p1*p2*(np.cosh(e1-e2)-np.cos(f1-f2)))
        return dict(l1_pt=p1,l2_pt=p2,l1_eta=e1,l2_eta=e2,l1_phi=f1,l2_phi=f2,m_l1l2=m,pt_l1l2=q)

    def test_equal_lepton_eta_gives_same_pair_rapidity(self):
        q,y,eta=reconstruct(self.pair(1.,1.))
        np.testing.assert_allclose(y,1.)
        self.assertTrue(np.all(eta>y))

    def test_longitudinal_reflection_and_azimuthal_rotation(self):
        q,y,eta=reconstruct(self.pair(.7,-1.2))
        qq,yy,ee=reconstruct(self.pair(-.7,1.2))
        np.testing.assert_allclose(qq,q); np.testing.assert_allclose(yy,-y); np.testing.assert_allclose(ee,-eta)
        qq,yy,ee=reconstruct(self.pair(.7,-1.2,.9))
        np.testing.assert_allclose(qq,q); np.testing.assert_allclose(yy,y); np.testing.assert_allclose(ee,eta)


if __name__=='__main__': unittest.main()
