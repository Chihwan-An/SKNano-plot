#!/usr/bin/env bash
exec /cvmfs/cms.cern.ch/common/cmssw-el9 -B /data6 -B /data9 -B /gv0 -- bash /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/pull_plot/combine/job_inner.sh "$@"
