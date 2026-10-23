#include <algorithm>
// Note that this is a template for MC, for data, it will automatically change uncessary lines in SKNano.py

void jx_Skim_HNWR_TWminusto2L2Nu_1() {
    HNWR module;
    module.SetRNTupleName("Events");
    module.SetAnalyzerName("HNWR");
    module.SetOutputThreads(1);
    module.LogEvery = 5000;
    module.IsDATA = false;
    module.MCSample = "ST_tW_top_Lep";
    module.xsec = 4.6651008780000005;
    module.sumW = 56972824.24992752;
    module.sumSign = 14997466.0;
    module.SetEra("2024");
    module.SetPeriod("");
module.Userflags = {
	"RFlav",
	"ZptNJet",
	"JetXcheck",
	"WeightSystOnly",
    };
	module.AddFile("/gv0/Users/achihwan/SkimNano15/2024/Skim_HNWR_TWminusto2L2Nu/tree_0.root");
	module.MaxEvent = std::max<Long64_t>(1, module.GetInputEntries()/1);
    module.SetOutfilePath("/gv0/Users/achihwan/SKNanoOutput_jetxcheck/Skim_HNWR_TWminusto2L2Nu/hists_1.root");
    module.SetFailurePolicy("fail-fast");
    module.SetMaxEventErrors(1);
    module.Init();
    module.initializeAnalyzer();
    module.Loop();
    module.WriteHist();
}
