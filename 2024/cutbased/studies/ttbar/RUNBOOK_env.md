# 실행 환경 런북 — cmssw-el9 컨테이너가 멈출 때 (2026-09-22 기록)

## 요약

`cmssw-el9` 래퍼를 쓰면 **컨테이너가 뜨기도 전에 영구히 멈춘다.**
`ai-tamsa1` 은 이미 EL9 이므로 **래퍼 없이 네이티브로 돌리면 된다.**

## 1. 증상

```bash
/cvmfs/cms.cern.ch/common/cmssw-el9 -B /data6 -B /data9 -B /gv0 -B /tmp -- bash <script>
```
→ 출력 한 줄도 없이 무한 대기. timeout 도 안 걸리고 ctrl-C 도 안 먹는다.

## 2. 원인

`/cvmfs/cms-ib.cern.ch` 가 **mount 는 살아 있는데 응답하지 않는다** (fuse 좀비).

```
$ mount | grep cms-ib
cvmfs2 on /cvmfs/cms-ib.cern.ch type fuse (ro,nosuid,nodev,relatime,...)   # 마운트는 보임
$ timeout 8 ls /cvmfs/cms-ib.cern.ch ; echo $?
124                                                                        # 응답 없음
```

그리고 `/cvmfs/cms.cern.ch/common/cmssw-env:103` 이 시작하자마자 그 저장소를 건드린다:

```bash
cvmfs_repos="cms cms-ib grid unpacked"
for repo in ${cvmfs_repos} ; do
  ls "${CVMFS_MOUNT}/${repo}.cern.ch" >/dev/null 2>&1 || true   # ← 여기서 박힘
done
```

`ls` 가 **D state (uninterruptible sleep)** 로 들어가므로 `2>/dev/null || true` 도, SIGKILL 도 소용없다.
D state 프로세스는 mount 가 복구되어야만 없어진다 (복구는 root 권한 필요: `cvmfs_config wipecache` / remount).

**이 상태는 2026-09-03 부터 계속되고 있었다.** 증거:

```
$ ps -o pid,lstart,etime,args -p 3818081
3818081 Thu Sep  3 22:20:41 2026  18-19:31:34  /bin/bash -e /cvmfs/.../cmssw-el9 ... run_pp.sh
$ ps --ppid 3818081 -o pid,etime,stat,args
3818114  18-19:31:34  D  ls /cvmfs/cms-ib.cern.ch
```

→ `BDT/SR/test/cbv15/run_pp.sh` 는 9/3 에 띄운 뒤 **한 번도 실행되지 않았다.**
(SR shapes 가 패치 이전 날짜 그대로인 것과 일치한다 — 06 §1 참조)

## 3. 진단 명령 (다음에 또 멈추면 이것부터)

```bash
# (a) 어느 저장소가 죽었나
for r in cms.cern.ch cms-ib.cern.ch unpacked.cern.ch grid.cern.ch; do
  printf '%-24s ' "$r"; timeout 8 ls /cvmfs/$r >/dev/null 2>&1 && echo OK || echo HUNG
done

# (b) 멈춘 프로세스가 정확히 무엇을 기다리는가  (<PID> = 멈춘 cmssw-el9)
ps --ppid <PID> -o pid,etime,stat,args        # STAT 가 D 면 I/O 에 박힌 것
cat /proc/<PID>/wchan; echo
```

## 4. 해결 — 컨테이너 없이 돌리기

`ai-tamsa1` (210.117.219.8) 은 **AlmaLinux 9.7 / kernel 5.14.0-611.11.1.el9_7 = EL9** 이다.
combine 이 빌드된 아키텍처와 같으므로 컨테이너가 애초에 필요 없다:

```
cmsos            -> el9_amd64
SCRAM_ARCH       -> el9_amd64_gcc12
combine          -> /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/combine
```

### 쓰는 법: `cmssw-el9 ... --` 부분만 지운다

```bash
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/ttbar/03_combine_validation

# 예전 (멈춤):
#   /cvmfs/cms.cern.ch/common/cmssw-el9 -B /data6 -B /data9 -B /gv0 -B /tmp -- bash $S/run_srcr_fit.sh ...

# 지금 (동작):
bash $S/run_fixture.sh
bash $S/run_cronly_fit.sh  cbv15_an2_ref_fixstream EE WR5000_N2500
bash $S/run_srcr_fit.sh    cbv15_an2_ref_fixstream EE WR5000_N2500
bash $S/run_blind_limit.sh cbv15_an2_ref_fixstream EE WR5000_N2500
```

스크립트 안의 `source /cvmfs/cms.cern.ch/cmsset_default.sh` + `scramv1 runtime -sh` 는 그대로 두면 된다.
`cms.cern.ch` 저장소는 정상이므로 cmsset 은 문제없다. **죽은 것은 `cms-ib` 하나뿐이다.**

오래 걸리는 것은 로그아웃에도 살아남게 — `nohup` 만으로는 부족하고 `setsid` 로 세션에서 떼어낸다:

```bash
setsid nohup bash $S/run_srcr_fit.sh cbv15_an2_ref_fixstream EE WR5000_N2500 \
  > $S/srcr_EE.log 2>&1 < /dev/null &
disown
```

(`nohup` 은 SIGHUP 만 막는다. 터미널이나 상위 셸이 프로세스 그룹째 죽이면 같이 죽는다.
`setsid` 를 붙이면 새 세션이 되어 살아남는다. 더 확실하게는 `tmux new -s fit` 안에서 돌린다.)

### 직접 셸을 쓰고 싶으면

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /data6/Users/achihwan/combine/CMSSW_14_1_0_pre4/src && eval $(scramv1 runtime -sh)
# 이제 combine / text2workspace.py / python3(ROOT) 사용 가능
```

## 5. 그래도 컨테이너가 필요하면

- **다른 호스트**: `ssh -p 1240 achihwan@210.117.219.6` — 사용자 확인으로 정상 동작.
  대규모/장시간 작업(run_pp, build_an2_cards)은 어차피 이쪽 condor 로 보내는 것이 맞다.
- **래퍼 우회**: `apptainer` / `singularity` 가 `/usr/bin` 에 있으므로 직접 호출 가능.
  단 `-B /cvmfs` 로 bind 하되 컨테이너 안에서 `cms-ib` 를 건드리지 말 것.
- **주의**: `cms-ib` 가 죽어 있는 한 `cmssw-el9`/`cmssw-cc7` 계열 래퍼는 이 호스트에서 전부 멈춘다
  (`cmssw-cc7:103` 에도 같은 줄이 있다).

## 6. 이번에 돌린 것 (2026-09-22, 완료)

CR + SR 동시 fit 을 위 방법으로 네이티브 실행 → **정상 종료.**

```
03_combine_validation/work_srcr/cbv15_an2_ref_fixstream_EE_WR5000_N2500/   작업 디렉터리
03_combine_validation/results_20260922/srcr_*.json  /  *.fit.log            결과 보관
```

`status 0`, rateParam 5개 전부 경계 안. 해석은 **`03_combine_validation/NOTES.md` §4**.
요약: 중심값은 CR-only 와 거의 같고 오차만 줄었다. 단 `covQual 2` 이고
`--saveWithUncertainties` 가 무시되어 **오차는 그대로 인용 불가** (`--robustHesse 1` 필요).
그리고 SR shapes 가 패치 이전이라 **SR 쪽 숫자는 잠정치** (06 §1).

### 재실행 / 이어서 돌리기

```bash
S=/data9/Users/achihwan/nano15/SKNanoAnalyzer/Nano15_Analyzers/plot/cutbased/studies/ttbar/03_combine_validation
W=$S/work_srcr/cbv15_an2_ref_fixstream_EE_WR5000_N2500

cat $W/srcr_result.json      # 결과
tail -20 $W/fit.log          # combine 로그

# MM 채널도 같은 방식으로
bash $S/run_srcr_fit.sh cbv15_an2_ref_fixstream MM WR5000_N2500
```

**재실행 전 주의**: 스크립트는 `[ -f ws.root ]` 로 text2workspace 를 건너뛴다.
중간에 죽었으면 **잘린 ws.root 가 남아 조용히 잘못된 결과를 낸다.**
`srcr_result.json` 도 `fit.root` 도 없는데 `ws.root` 만 있으면 `rm -f $W/ws.root` 후 다시 돌릴 것.

text2workspace.py 는 이 card (12채널, 수백 nuisance) 에서 **약 6분** 걸리고
**끝날 때까지 `t2w.log` 가 0 바이트다** — 멈춘 것이 아니다.
진행 확인은 로그가 아니라 프로세스로: `ps -o pid,etime,args -p <pid>`.
