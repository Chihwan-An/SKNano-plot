#include <algorithm>
// Note that this is a template for MC, for data, it will automatically change uncessary lines in SKNano.py

void jx_Skim_HNWR_DYto2L_4Jets_Bin_HT_100to400_MLL_120_4() {
    HNWR module;
    module.SetRNTupleName("Events");
    module.SetAnalyzerName("HNWR");
    module.SetOutputThreads(1);
    module.LogEvery = 5000;
    module.IsDATA = false;
    module.MCSample = "DYto2L_MLL120toInf_HT100to400";
    module.xsec = 4.383709336;
    module.sumW = 586525118.1059303;
    module.sumSign = 18974607.0;
    module.SetEra("2024");
    module.SetPeriod("");
module.Userflags = {
	"RFlav",
	"ZptNJet",
	"JetXcheck",
	"WeightSystOnly",
    };
	module.AddFile("/gv0/Users/achihwan/SkimNano15/2024/Skim_HNWR_DYto2L-4Jets_Bin-HT-100to400-MLL-120/tree_11.root");
	module.MaxEvent = std::max<Long64_t>(1, module.GetInputEntries()/1);
    module.SetOutfilePath("/gv0/Users/achihwan/SKNanoOutput_jetxcheck/Skim_HNWR_DYto2L-4Jets_Bin-HT-100to400-MLL-120/hists_4.root");
    module.SetFailurePolicy("fail-fast");
    module.SetMaxEventErrors(1);
    module.Init();
    module.initializeAnalyzer();
    module.Loop();
    module.WriteHist();
}
