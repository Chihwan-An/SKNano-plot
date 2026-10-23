for tag in cbv15_an2_ref_fixstream cbv15_an2_ref; do for ch in EE MM; do for mp in WR5000_N2500 WR5000_N200; do
  echo "== $tag $ch $mp"; bash /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/BDT/SR/test/ttfit_validation/run_blind_limit.sh $tag $ch $mp /tmp/claude-5596/-data9-Users-achihwan-25-020-AN-25-020/b8b0160d-1e48-4158-a446-356682ce195b/scratchpad/ttfit/blind 2>&1 | tail -6
done; done; done
echo ALL_LIMITS_DONE
