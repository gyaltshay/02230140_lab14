# CTE412 Practical 15 (Lab 14) — Campus Notice Board Releases
**Student number:** 02230140  
**Full name:** Pasang Gyeltshen  
**Repository:** https://github.com/gyaltshay/02230140_lab14

## 1. Objective
Measure availability during Recreate, RollingUpdate, failed rollout/rollback, blue/green switching and a ConfigMap feature-flag change, using requests emitted by a continuous Kubernetes monitor rather than assumptions.

## 2. Environment
Windows / PowerShell [CONFIRM], Docker version [COMMAND OUTPUT], kind version [COMMAND OUTPUT], kubectl client and cluster version [COMMAND OUTPUT]. Application: Python 3.12 on Alpine; monitor: BusyBox. Cluster `cte412-02230140`, namespace `nb-02230140`.

## 3. Results
**Complete only with measured data from your own `evidence/` files. Do not copy the sample numbers from the reference PDF.**

| Change | Requests observed | Failed requests | Mixed-version window (s) | Peak notice-board Pods |
|---|---:|---:|---:|---:|
| Recreate 1.0.0 → 1.1.0 | TBD | TBD | TBD | TBD |
| RollingUpdate 1.0.0 → 1.1.0 | TBD | TBD | TBD | TBD |
| Broken 1.2.0 → rollback | TBD | TBD | TBD | TBD |
| Blue → green | TBD | TBD | TBD | TBD |
| Green → blue | TBD | TBD | TBD | TBD |
| Blue → green | TBD | TBD | TBD | TBD |
| FEATURE_PINNED false → true | TBD | TBD | N/A (same version) | TBD |

## 4. Analysis
**A1. Rank strategies by failed requests.** Use `evidence/t5-recreate-summary.txt`, `t5-rolling-summary.txt`, `t6-summary.txt`, `t7-summary.txt`, and `t8-summary.txt`. Explain any observed FAIL windows.

**A2. Broken release.** Explain readiness `/healthz`, liveness `/version`, `maxUnavailable: 0`, `maxSurge: 1`, `minReadySeconds: 5`, and `progressDeadlineSeconds: 60` with your observed `Progressing` condition and monitor log. Discuss defaults accurately using your actual cluster.

**A3. RollingUpdate vs blue/green.** Compare your mixed-version response interval (not only Pod overlap), peak Pod count and quota, and actual time to revert to stable traffic.

**A4. Recreate use case.** Explain a genuine incompatibility such as a singleton worker that cannot coexist with the previous version.

**A5. Feature flag.** Explain that the code and image are unchanged; ConfigMap-provided environment variables do not update in running containers, so a declarative Pod-template change is required.

## 5. Reflection
**Actual error:** [YOUR ERROR AND COMMAND OUTPUT]  
**Diagnosis and fix:** [WHAT YOU DID AND WHY]  
**Still unclear:** [YOUR OWN QUESTION]

## 6. References
Document sources you actually consulted, including access date:
- Kubernetes Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- Kubernetes Probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- Kubernetes Services: https://kubernetes.io/docs/concepts/services-networking/service/
- Kubernetes ConfigMaps: https://kubernetes.io/docs/concepts/configuration/configmap/
- kind: https://kind.sigs.k8s.io/
