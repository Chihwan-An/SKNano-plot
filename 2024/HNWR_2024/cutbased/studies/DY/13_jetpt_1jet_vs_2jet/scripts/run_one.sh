#!/bin/bash
unset CONDA_PREFIX CONDA_DEFAULT_ENV CONDA_PROMPT_MODIFIER CONDA_SHLVL
unset MAMBA_EXE
export PATH=/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export MAMBA_ROOT_PREFIX=/opt/conda
# /opt/conda/bin lives inside the singularity image the batch jobs run in.
# The same script is also run by hand on a login node, where that prefix does
# not exist, so fall back to the micromamba the submitting shell used.
if ! command -v micromamba > /dev/null 2>&1; then
    export PATH=/data6/Users/achihwan/.local/bin:$PATH
    export MAMBA_ROOT_PREFIX=/data6/Users/achihwan/micromamba
fi
if ! command -v micromamba > /dev/null 2>&1; then
    echo "micromamba not found in /opt/conda/bin nor /data6/Users/achihwan/.local/bin" >&2
    exit 1
fi
eval "$(micromamba shell hook -s bash)"
if [ -d "${MAMBA_ROOT_PREFIX}/envs/Nano15" ]; then
    micromamba activate Nano15 || exit 1
else
    micromamba activate /data6/Users/achihwan/micromamba/envs/Nano15 || exit 1
fi

export SKNANO_HOME=/data9/Users/achihwan/nano15/SKNanoAnalyzer
export SKNANO_DATA=/data9/Users/achihwan/nano15/SKNanoAnalyzer/data/Run3_v15_Run2_v15
export SKNANO_BIN=$SKNANO_HOME/bin
export PYTHONPATH=$PYTHONPATH:$SKNANO_HOME/python

export PATH=$PATH:/data9/Users/achihwan/nano15/SKNanoAnalyzer/external/lhapdf/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data9/Users/achihwan/nano15/SKNanoAnalyzer/external/lhapdf/redhat/lib
export LHAPDF_INCLUDE_DIR=/data9/Users/achihwan/nano15/SKNanoAnalyzer/external/lhapdf/redhat/include
export LHAPDF_LIB_DIR=/data9/Users/achihwan/nano15/SKNanoAnalyzer/external/lhapdf/redhat/lib
export CORRECTION_INCLUDE_DIR=`correction config --incdir`
export CORRECTION_LIB_DIR=`correction config --libdir`
export JSONPOG_REPO_PATH=/data9/Users/achihwan/nano15/SKNanoAnalyzer/CMS_corrections
export ROCCOR_PATH=/data9/Users/achihwan/nano15/SKNanoAnalyzer/external/RoccoR
export ONNXRUNTIME_INCLUDE_DIR=${CONDA_PREFIX}/include/onnxruntime/core/session
export ONNXRUNTIME_LIB_DIR=${CONDA_PREFIX}/lib

I=/data9/Users/achihwan/nano15/SKNanoAnalyzer/install/redhat
export LD_LIBRARY_PATH=$I/lib:${CONDA_PREFIX}/lib:/data9/Users/achihwan/nano15/SKNanoAnalyzer/external/lhapdf/redhat/lib:$CORRECTION_LIB_DIR
export ROOT_HIST=0
export ROOT_INCLUDE_PATH=$I/include
cd /data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/HNWR_2024/cutbased/studies/DY/13_jetpt_1jet_vs_2jet/jobs
root -l -b -q $1.cc > $1.log 2>&1
echo "$1 rc=$?"
