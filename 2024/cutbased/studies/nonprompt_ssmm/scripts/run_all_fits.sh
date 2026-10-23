#!/usr/bin/env bash
# run every fit/<tag> (not _smoke*) on tamsa2; each writes fit_result.json next to its card
ST=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/nonprompt_ssmm
for d in $ST/fit/*/; do
  t=$(basename $d); case $t in _*) continue;; esac
  [ -n "${ONLY:-}" ] && [[ $t != *$ONLY* ]] && continue
  echo "== $t"; bash $ST/scripts/run_asimov_fit.sh $d 2>&1 | tail -1
done
