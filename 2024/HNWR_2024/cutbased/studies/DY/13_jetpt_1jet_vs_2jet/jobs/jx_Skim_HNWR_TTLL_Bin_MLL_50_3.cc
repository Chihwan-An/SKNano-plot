#include <algorithm>
// Note that this is a template for MC, for data, it will automatically change uncessary lines in SKNano.py

void jx_Skim_HNWR_TTLL_Bin_MLL_50_3() {
    HNWR module;
    module.SetRNTupleName("Events");
    module.SetAnalyzerName("HNWR");
    module.SetOutputThreads(1);
    module.LogEvery = 5000;
    module.IsDATA = false;
    module.MCSample = "ttZtoLL_MLL50toInf";
    module.xsec = 0.08646;
    module.sumW = 340956.55011084676;
    module.sumSign = 2054714.0;
    module.SetEra("2024");
    module.SetPeriod("");
module.Userflags = {
	"RFlav",
	"ZptNJet",
	"JetXcheck",
	"WeightSystOnly",
    };
	module.AddFile("/gv0/Users/achihwan/SkimNano15/2024/Skim_HNWR_TTLL_Bin-MLL-50/tree_2.root");
	module.MaxEvent = std::max<Long64_t>(1, module.GetInputEntries()/1);
    module.SetOutfilePath("/gv0/Users/achihwan/SKNanoOutput_jetxcheck/Skim_HNWR_TTLL_Bin-MLL-50/hists_3.root");
    module.SetFailurePolicy("fail-fast");
    module.SetMaxEventErrors(1);
    module.Init();
    module.initializeAnalyzer();
    module.Loop();
    module.WriteHist();
}
