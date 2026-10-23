#include <algorithm>
// Note that this is a template for MC, for data, it will automatically change uncessary lines in SKNano.py

void jx_Skim_HNWR_TTto2L2Nu_TuneCP5_5() {
    HNWR module;
    module.SetRNTupleName("Events");
    module.SetAnalyzerName("HNWR");
    module.SetOutputThreads(1);
    module.LogEvery = 5000;
    module.IsDATA = false;
    module.MCSample = "TTLL_powheg";
    module.xsec = 98.03611310400001;
    module.sumW = 37820110815.09285;
    module.sumSign = 466316813.0;
    module.SetEra("2024");
    module.SetPeriod("");
module.Userflags = {
	"RFlav",
	"ZptNJet",
	"JetXcheck",
	"WeightSystOnly",
    };
	module.AddFile("/gv0/Users/achihwan/SkimNano15/2024/Skim_HNWR_TTto2L2Nu_TuneCP5/tree_101.root");
	module.MaxEvent = std::max<Long64_t>(1, module.GetInputEntries()/1);
    module.SetOutfilePath("/gv0/Users/achihwan/SKNanoOutput_jetxcheck/Skim_HNWR_TTto2L2Nu_TuneCP5/hists_5.root");
    module.SetFailurePolicy("fail-fast");
    module.SetMaxEventErrors(1);
    module.Init();
    module.initializeAnalyzer();
    module.Loop();
    module.WriteHist();
}
