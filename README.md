# CTE412 Practical 15 (Lab 14) — Student 02230140

**Original reproducible project; no borrowed screenshots or test results.**

## Requirements
Windows PowerShell, Docker Desktop, kind, kubectl, Git, Git Bash (to execute the AWK summary script). The namespace annotation uses Pasang Gyeltshen. All new image tags and resources include `02230140`.

## Important
Do **not** stop/recreate `monitor` during Tasks 4–8. Only `kubectl rollout undo` in Task 6 is an allowed imperative application state change. Perform remaining state transitions by editing/applying manifests. `kubectl get`, `describe`, `logs`, and `rollout status` are observational. To meet the assessed text-evidence rules, save actual stdout into `evidence/tN-...txt` files; no evidence files have been pre-filled.

## Full initial build and cluster setup (PowerShell in repository root)
```powershell
kind create cluster --name cte412-02230140 --config cluster/kind-cluster.yaml
kubectl apply -f manifests/base/namespace.yaml
kubectl apply -f manifests/base/quota.yaml
kubectl apply -f manifests/base/limitrange.yaml
kubectl config set-context --current --namespace=nb-02230140
kubectl get nodes -o wide | Out-File -Encoding utf8 evidence/t1-nodes.txt
kubectl describe quota nb-quota | Out-File -Encoding utf8 evidence/t1-quota.txt
kubectl config view --minify | Out-File -Encoding utf8 evidence/t1-context.txt
$versions = @('1.0.0','1.1.0','1.2.0-broken')
foreach ($v in $versions) {
  docker build -t "notice-board:02230140-$v" --build-arg "APP_VERSION=$v" --build-arg STUDENT_ID=02230140 app
  kind load docker-image "notice-board:02230140-$v" --name cte412-02230140
}
docker images notice-board | Out-File -Encoding utf8 evidence/t2-images.txt
docker exec cte412-02230140-worker crictl images | Select-String notice-board | Out-File -Encoding utf8 evidence/t2-node-images.txt
```

## Task 2: Verify warm-up (run quickly after container starts)
```powershell
docker run --rm -d --name nb-local -p 8080:8080 notice-board:02230140-1.0.0
curl.exe -si http://localhost:8080/version | Out-File -Encoding utf8 evidence/t2-version.txt
curl.exe -si http://localhost:8080/healthz | Out-File -Encoding utf8 evidence/t2-health-early.txt
Start-Sleep -Seconds 6
curl.exe -si http://localhost:8080/healthz | Out-File -Encoding utf8 evidence/t2-health-later.txt
docker stop nb-local
```
If the first request takes five seconds or more, repeat to capture a genuine initial HTTP 503 response.

## Task 3: Baseline and host testing
```powershell
kubectl apply -f manifests/rolling/03-baseline.yaml
kubectl apply -f manifests/rolling/services.yaml
kubectl rollout status deployment/notice-board
kubectl get deployment,rs,pods -l app=notice-board -o wide | Out-File -Encoding utf8 evidence/t3-workloads.txt
kubectl get endpointslice -l kubernetes.io/service-name=notice-board -o yaml | Out-File -Encoding utf8 evidence/t3-endpoints.txt
1..12 | ForEach-Object { curl.exe -s http://127.0.0.1:30090/version; Start-Sleep -Milliseconds 250 } | Out-File -Encoding utf8 evidence/t3-host.txt
```
Confirm that `evidence/t3-host.txt` contains at least two distinct `pod` values.

## Task 4: Begin uninterrupted availability monitoring
```powershell
kubectl apply -f manifests/base/monitor.yaml
kubectl get pod monitor
Start-Sleep -Seconds 65
kubectl logs monitor --since=60s | Out-File -Encoding utf8 evidence/t4-atrest.log
Get-Content evidence/t4-atrest.log -TotalCount 10 | Out-File -Encoding utf8 evidence/t4-first10.txt
```
In **Git Bash**, run `sh scripts/summarise.sh evidence/t4-atrest.log > evidence/t4-summary.txt`. If failures occur at rest, diagnose and resolve them before proceeding.

## Task 5: Recreate and RollingUpdate
For each event, record `$start=Get-Date -Format o`; sleep 10 s **before** applying; after `kubectl rollout status`, sleep another 10 s; save log from actual event window. Example below uses full live log to guarantee coverage; you can additionally extract the individual window from timestamped log lines for accurate counts.
```powershell
Start-Sleep 10
kubectl apply -f manifests/rolling/05-recreate.yaml
kubectl rollout status deployment/notice-board
Start-Sleep 10
kubectl logs monitor | Out-File -Encoding utf8 evidence/t5-recreate-full.log

kubectl apply -f manifests/rolling/03-baseline.yaml
kubectl rollout status deployment/notice-board

# In another PowerShell window before applying rolling release:
# kubectl get pods -l app=notice-board -w | Tee-Object evidence/t5-pods-watch.txt
Start-Sleep 10
kubectl apply -f manifests/rolling/05-rolling.yaml
kubectl rollout status deployment/notice-board
Start-Sleep 10
kubectl logs monitor | Out-File -Encoding utf8 evidence/t5-rolling-full.log
kubectl rollout history deployment/notice-board | Out-File -Encoding utf8 evidence/t5-history.txt
```
**Important:** Full cumulative logs include earlier releases. Do not use a cumulative log to calculate one release's metrics. Filter to the event's start/end timestamps (or capture a `--since-time` window recorded before the event), then summarise with Git Bash. The 0.5-second monitor may lose a request during a Service endpoint switch: report actual values, not expected ones.

## Task 6: Broken release and rollback
```powershell
Start-Sleep 10
kubectl apply -f manifests/rolling/06-broken.yaml
kubectl rollout status deployment/notice-board --timeout=90s
kubectl describe deployment notice-board | Out-File -Encoding utf8 evidence/t6-conditions.txt
kubectl get pods -l app=notice-board -o wide | Out-File -Encoding utf8 evidence/t6-pods.txt
kubectl rollout undo deployment/notice-board
kubectl rollout status deployment/notice-board
Start-Sleep 10
kubectl logs monitor | Out-File -Encoding utf8 evidence/t6-monitor-full.log
```
The allowed undo operation rolls back live state. Afterwards, align the desired manifest to the observed live image/labels and run `kubectl diff -f <matching-manifest>`. DO NOT reapply a mismatching manifest which changes the live rollout again. Save evidence proving live/template agreement.

## Task 7: Dual colour switches
First replace the original `notice-board` Deployment **declaratively**, not by `kubectl delete`: prune only the targeted rolling Deployment after both colours exist, with a carefully constrained apply/prune allowlist or a tracked removal manifest. Verify replica quota before switching. Create final blue/green objects:
```powershell
kubectl apply -f manifests/bluegreen/flags.yaml
kubectl apply -f manifests/bluegreen/deployments.yaml
kubectl rollout status deployment/notice-board-blue
kubectl rollout status deployment/notice-board-green
kubectl apply -f manifests/bluegreen/services-blue.yaml
kubectl get endpointslice -o wide | Out-File -Encoding utf8 evidence/t7-endpoints-before.txt
kubectl apply -f manifests/base/preview-test.yaml
kubectl logs preview-test | Out-File -Encoding utf8 evidence/t7-preview.txt
```
With **monitor still running**, apply services-green.yaml (first switch), services-blue.yaml (second switch), services-green.yaml (third switch). Record each apply time and capture event-window monitor logs. Confirm production `1.0.0 → 1.1.0 → 1.0.0 → 1.1.0` and preview always `1.1.0`. Save endpoint and quota evidence.

## Task 8: Feature flag
Before doing this, verify green production serves `pinnedFirst:false`:
```powershell
curl.exe -s http://127.0.0.1:30090/notices | Out-File -Encoding utf8 evidence/t8-notices-before.txt
```
Edit `manifests/bluegreen/flags.yaml` to `FEATURE_PINNED: 'true'`, then `kubectl apply -f manifests/bluegreen/flags.yaml`. Save another response, confirming that running Pods still use `false`. Edit the green Deployment's `cte412/flag-revision` annotation **from '1' to '2'**, apply its full manifest, and wait for `kubectl rollout status deployment/notice-board-green`. After ten seconds, capture true response and monitor evidence; verify zero failures from your measured window.

## Task 9: Rebuild and cleanup
Save `kubectl logs monitor` to `evidence/t9-monitor-full.log` before any deletion. The final repo manifests must be in Task-8 state (flags true, green annotation 2, production green). Preserve namespace, quota, and LimitRange while declaratively removing other resources. Recreate the final state by applying `monitor.yaml`, `flags.yaml`, `deployments.yaml`, and `services-green.yaml`; capture created-object output. Confirm production version 1.1.0 and `pinnedFirst: true`. Finally:
```powershell
kubectl config set-context --current --namespace=default
kind delete cluster --name cte412-02230140
kind get clusters | Out-File -Encoding utf8 evidence/t9-cluster-deleted.txt
```
Commit after **each** task and push to your own repository when evidence and report are complete.

## Submission
Repository URL: https://github.com/gyaltshay/02230140_lab14
The required report is `report/p06-report.md`. Replace all TBD cells with measured values. The original lab's assessment requires output evidence named `tN-...` under `evidence/` and student ID 02230140 in identity-sensitive outputs.
