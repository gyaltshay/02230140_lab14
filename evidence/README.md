# Original practical evidence
Store actual terminal output from your own cluster here. Required files must show SID 02230140. The folder intentionally contains no fabricated logs or screenshots.
Use `kubectl logs monitor --timestamps=false | Set-Content -Encoding utf8 evidence\t9-monitor-full.log` on PowerShell 7, or `Out-File -Encoding utf8` on Windows PowerShell.
Record task start and end timestamps, then extract time-window logs before running the summariser. Confirm every measured log begins at least 10 seconds before applying a release and ends at least 10 seconds after rollout completion.
