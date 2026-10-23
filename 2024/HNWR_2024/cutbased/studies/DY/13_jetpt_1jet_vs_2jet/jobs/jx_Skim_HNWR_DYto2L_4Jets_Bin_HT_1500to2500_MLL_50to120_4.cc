#include <algorithm>
// Note that this is a template for MC, for data, it will automatically change uncessary lines in SKNano.py

void jx_Skim_HNWR_DYto2L_4Jets_Bin_HT_1500to2500_MLL_50to120_4() {
    HNWR module;
    module.SetRNTupleName("Events");
    module.SetAnalyzerName("HNWR");
    module.SetOutputThreads(1);
    module.LogEvery = 5000;
    module.IsDATA = false;
    module.MCSample = "DYto2L_MLL50to120_HT1500to2500";
    module.xsec = 0.065423511;
    module.sumW = 1084303.5956919193;
    module.sumSign = 1889567.0;
    module.SetEra("2024");
    module.SetPeriod("");
module.Userflags = {
	"RFlav",
	"ZptNJet",
	"JetXcheck",
	"WeightSystOnly",
    };
	module.AddFile("/gv0/Users/achihwan/SkimNano15/2024/Skim_HNWR_DYto2L-4Jets_Bin-HT-1500to2500-MLL-50to120/tree_3.root");
	module.MaxEvent = std::max<Long64_t>(1, module.GetInputEntries()/1);
    module.SetOutfilePath("/gv0/Users/achihwan/SKNanoOutput_jetxcheck/Skim_HNWR_DYto2L-4Jets_Bin-HT-1500to2500-MLL-50to120/hists_4.root");
    module.SetFailurePolicy("fail-fast");
    module.SetMaxEventErrors(1);
    module.Init();
    module.initializeAnalyzer();
    module.Loop();
    module.WriteHist();
}
