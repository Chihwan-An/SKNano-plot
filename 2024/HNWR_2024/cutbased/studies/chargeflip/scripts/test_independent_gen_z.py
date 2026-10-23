import unittest
from pathlib import Path
import math
import ROOT

ROOT.gInterpreter.Declare(Path(__file__).with_name('independent_gen_z.hxx').read_text())


def vec(values,kind='float'):
    v=ROOT.VecOps.RVec(kind)()
    for x in values: v.push_back(x)
    return v


class IndependentGenZTest(unittest.TestCase):
    def call(self,pt,eta,phi,mass,pid,status,flags,jpt=(),jeta=(),jphi=()):
        return list(ROOT.IndependentDY.direction(vec(pt),vec(eta),vec(phi),vec(mass),
            vec(pid,'int'),vec(status,'int'),vec(flags,'unsigned short'),
            vec(jpt),vec(jeta),vec(jphi)))

    def test_no_lepton_required_and_jet_acceptance(self):
        r=self.call([30],[2],[0],[91],[23],[62],[0],
                    [40,41,60,80],[0,0,3,5],[0,0,0,0])
        self.assertEqual(r[5],1)
        self.assertAlmostEqual(r[3],2)
        self.assertEqual(r[6:8],[1,2])
        self.assertAlmostEqual(r[4],math.asinh(30*math.sinh(2)/math.hypot(91,30)))

    def test_prompt_lepton_jet_cleaning_without_lepton_pt_cut(self):
        r=self.call([30,1],[0,1],[0,1],[91,0],[23,11],[62,1],[0,1],
                    [50,50],[1,0],[1,0])
        self.assertEqual(r[6:8],[1,1])

    def test_hard_pair_fallback(self):
        r=self.call([50,50],[0,0],[0,math.pi],[0,0],[11,-11],[23,23],[128,128])
        self.assertEqual(r[5],3)
        self.assertAlmostEqual(r[0],100,places=5)

    def test_missing_and_ambiguous_bosons_are_flagged(self):
        r=self.call([30,30],[0,0],[0,0],[91,91],[23,23],[62,62],[0,0])
        self.assertEqual(r[5],0)
        self.assertEqual(r[8],2)
        self.assertTrue(math.isnan(r[3]))

    def test_zero_pt_eta_not_defined(self):
        r=self.call([0],[0],[0],[91],[23],[62],[0])
        self.assertTrue(math.isnan(r[3]))
        self.assertEqual(r[4],0)


if __name__=='__main__': unittest.main()
