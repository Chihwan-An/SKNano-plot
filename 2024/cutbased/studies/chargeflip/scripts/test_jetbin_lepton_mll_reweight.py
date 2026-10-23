"""Numerical derivative checks for fitted-weight and target covariance."""
import unittest

import numpy as np

from jetbin_lepton_mll_reweight import comparison, weighted_feature


class ReweightTest(unittest.TestCase):
    def test_covariance_against_finite_difference(self):
        s=np.array([[12.,5.,3.],[4.,11.,5.]])
        t=np.array([[7.,8.,3.],[9.,6.,11.]])
        vs=s*1.7; vt=t*2.3
        d=comparison(s,vs,t,vt)
        x=np.concatenate((s.ravel(),t.ravel()))
        def evaluate(x):
            ss=x[:6].reshape(2,3); tt=x[6:].reshape(2,3)
            pred=(ss*tt.sum(axis=1)[:,None]/ss.sum(axis=1)[:,None]).sum(axis=0)
            return np.concatenate((pred/pred.sum(),tt.sum(axis=0)/tt.sum()))
        jac=np.empty((6,12)); step=1e-4
        for i in range(len(x)):
            xp=x.copy(); xm=x.copy(); xp[i]+=step; xm[i]-=step
            jac[:,i]=(evaluate(xp)-evaluate(xm))/(2*step)
        cov=(jac*np.concatenate((vs.ravel(),vt.ravel())))@jac.T
        np.testing.assert_allclose(d['cov_after'],cov[:3,:3],rtol=1e-8,atol=1e-12)
        np.testing.assert_allclose(d['cov_target'],cov[3:,3:],rtol=1e-8,atol=1e-12)
        np.testing.assert_allclose(d['cov_after_target'],cov[:3,3:],rtol=1e-8,atol=1e-12)
        for key in ('before','after','target'):
            self.assertAlmostEqual(d[key].sum(),1)
            self.assertGreaterEqual(np.linalg.eigvalsh(d[f'cov_{key}']).min(),-1e-12)
        values=np.array([.2,1.1,2.4])
        def moments(h,v):
            return np.stack((h.sum(axis=1),v.sum(axis=1),h@values,v@values,v@(values**2)),axis=1)
        feature=weighted_feature(moments(s,vs),moments(t,vt))
        self.assertAlmostEqual(feature['value'],np.dot(d['after'],values))
        self.assertAlmostEqual(feature['error']**2,values@d['cov_after']@values)

    def test_mll_exact_match_and_correlated_error_cancellation(self):
        # Each observable bin equals one mll bin: prediction equals target even
        # under statistical perturbations. Ratio error must therefore be zero.
        s=np.diag([12.,18.,30.]); t=np.diag([24.,9.,10.])
        d=comparison(s,s*1.4,t,t*2.)
        np.testing.assert_allclose(d['after'],d['target'],atol=1e-14)
        np.testing.assert_allclose(d['ratios'][1],1)
        np.testing.assert_allclose(d['errors'][1],0,atol=1e-8)


if __name__=='__main__':
    unittest.main()
