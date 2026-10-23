"""Test independent-sample error propagation and transfer-bin coverage."""
import unittest
import numpy as np

from jetbin_lepton_zpt_reweight import independent_comparison, independent_feature, make_groups, aggregate


class RecoilTransferTest(unittest.TestCase):
    def test_independent_covariance(self):
        s=np.array([[12.,5.,3.],[4.,11.,5.]])
        t=np.array([[7.,8.,3.],[9.,6.,11.]])
        vs=s*1.7; vt=t*2.3
        f=np.array([.7,1.3]); fv=np.array([.03,.07])
        d=independent_comparison(s,vs,t,vt,f,fv)
        x=np.concatenate((s.ravel(),t.ravel(),f))
        def evaluate(x):
            ss=x[:6].reshape(2,3); tt=x[6:12].reshape(2,3); ff=x[12:]
            pp=(ss*ff[:,None]).sum(axis=0)
            return np.concatenate((pp/pp.sum(),tt.sum(axis=0)/tt.sum()))
        jac=np.empty((6,len(x))); step=1e-4
        for i in range(len(x)):
            xp=x.copy(); xm=x.copy(); xp[i]+=step; xm[i]-=step
            jac[:,i]=(evaluate(xp)-evaluate(xm))/(2*step)
        cov=(jac*np.concatenate((vs.ravel(),vt.ravel(),fv)))@jac.T
        np.testing.assert_allclose(d['cov_after'],cov[:3,:3],rtol=1e-7,atol=1e-12)
        np.testing.assert_allclose(d['cov_target'],cov[3:,3:],rtol=1e-7,atol=1e-12)
        np.testing.assert_allclose(d['cov_after_target'],cov[:3,3:],atol=1e-12)
        values=np.array([.2,1.1,2.4])
        moments=np.stack((s.sum(axis=1),vs.sum(axis=1),s@values,vs@values,vs@(values**2)),axis=1)
        feature=independent_feature(moments,f,fv)
        self.assertAlmostEqual(feature['value'],np.dot(d['after'],values))
        self.assertAlmostEqual(feature['error']**2,values@d['cov_after']@values)

    def test_groups_preserve_all_cells(self):
        s=np.array([[0.,100,100,3,2],[40,30,30,1,0]])
        t=np.array([[1.,90,110,0,1],[45,25,31,0,1]])
        for mode in ('zpt','mll','mll_zpt'):
            groups=make_groups(s,s,t,t,mode,50)
            np.testing.assert_array_equal(np.sort(np.concatenate(groups)),np.arange(s.size))
            for h in (s,t):
                grouped=aggregate(h,groups)
                self.assertAlmostEqual(grouped.sum(),h.sum())
                self.assertTrue(np.all(grouped>=50))


if __name__=='__main__': unittest.main()
