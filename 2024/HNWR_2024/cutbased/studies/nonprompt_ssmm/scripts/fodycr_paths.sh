# sourced by run_skim_fodycr.sh / submit_ready_fodycr.sh: where one sample of the FOMode,FODYCR,RFlav production lives
RL_MC=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_091846_HNWR_FOMode_FODYCR_RFlav/2024
OUT_MC=/gv0/Users/achihwan/SKNanoOutput/HNWR/backup/FOMode_FODYCR_RFlav/2024
RL_DATA=/gv0/Users/achihwan/SKNanoRunlog/2026_09_24_104852_HNWR_FOMode_FODYCR_RFlav/2024   # data re-submitted first (2026-09-24 10:48)
OUT_DATA=/gv0/Users/achihwan/SKNanoOutput_fodata/HNWR/FOMode_FODYCR_RFlav/2024
# fo_src <sample> -> prints "file <merged.root>" or "glob <per-job glob>" when complete, nothing otherwise
fo_src() {
  local s=$1 rl out
  case $s in *Muon*) rl=$RL_DATA; out=$OUT_DATA;; *) rl=$RL_MC; out=$OUT_MC;; esac
  if [ -f $out/$s.root ] && [ -f $rl/$s/hadd.out ]; then echo "file $out/$s.root"; return; fi
  local nj no; nj=$(ls $rl/$s/job_*.cc 2>/dev/null | wc -l); no=$(ls $rl/$s/output/hists_*.root 2>/dev/null | wc -l)
  [ "$nj" -gt 0 ] && [ "$nj" -eq "$no" ] && echo "glob $rl/$s/output/hists_*.root"
}
