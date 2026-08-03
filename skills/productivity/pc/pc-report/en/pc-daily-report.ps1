# Daily PC Monitoring Report - Windows (PowerShell)
# Uses native tools (CIM/WMI, Get-Counter, Get-Process) to summarize CPU, RAM, disk.
#
# Windows has no built-in 24h history like Linux sysstat/sar, so this is a
# point-in-time snapshot at run time. Output mirrors the Linux report format.
#
# Run:  powershell -ExecutionPolicy Bypass -File .\pc-daily-report.ps1
#   or (PowerShell 7+):  pwsh -File ./pc-daily-report.ps1

$ErrorActionPreference = 'SilentlyContinue'
$OutputEncoding = [System.Text.Encoding]::UTF8

$HostName = $env:COMPUTERNAME
$Today    = Get-Date -Format 'yyyy-MM-dd HH:mm'
$os       = Get-CimInstance Win32_OperatingSystem
$cpuInfo  = Get-CimInstance Win32_Processor | Select-Object -First 1
$nCpu     = ($cpuInfo.NumberOfLogicalProcessors)

Write-Output "----------------------------------------"
Write-Output "  DAILY REPORT — $HostName (Windows)"
Write-Output "  $Today"
Write-Output "----------------------------------------"
Write-Output ""
Write-Output "[i] Snapshot at run time (Windows has no sar history)."
Write-Output ""

# -- UPTIME & LOAD --
$boot   = $os.LastBootUpTime
$uptime = (Get-Date) - $boot
Write-Output "UPTIME & LOAD"
Write-Output ("up {0}d {1}h {2}min (since {3:yyyy-MM-dd HH:mm})" -f $uptime.Days, $uptime.Hours, $uptime.Minutes, $boot)
Write-Output ""

# -- CPU --
Write-Output "-- CPU — $nCpu logical cores ($($cpuInfo.Name.Trim())) --"
$cpuLoad = (Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 2 |
            Select-Object -ExpandProperty CounterSamples |
            Select-Object -Last 1).CookedValue
if ($null -eq $cpuLoad) { $cpuLoad = $cpuInfo.LoadPercentage }
$cpuUse  = [math]::Round($cpuLoad, 1)
$cpuIdle = [math]::Round(100 - $cpuLoad, 1)
Write-Output ("> Snapshot — Used: {0}% | Idle: {1}%" -f $cpuUse, $cpuIdle)
Write-Output ""

# -- RAM --
$totalKb = $os.TotalVisibleMemorySize
$freeKb  = $os.FreePhysicalMemory
$usedKb  = $totalKb - $freeKb
$totalGiB = [math]::Round($totalKb / 1MB, 1)
$usedPct  = [math]::Round($usedKb / $totalKb * 100, 1)
$freeMb   = [math]::Round($freeKb / 1KB, 0)
$usedMb   = [math]::Round($usedKb / 1KB, 0)
Write-Output "-- RAM — $totalGiB GiB total --"
Write-Output ("> Usage: {0}%  ({1} MB used | {2} MB free)" -f $usedPct, $usedMb, $freeMb)

$pageTotal = $os.SizeStoredInPagingFiles
$pageFree  = $os.FreeSpaceInPagingFiles
if ($pageTotal) {
    $pageUsedMb = [math]::Round(($pageTotal - $pageFree) / 1KB, 0)
    $pageTotMb  = [math]::Round($pageTotal / 1KB, 0)
    Write-Output ("> Paging — Used: {0} MB / {1} MB" -f $pageUsedMb, $pageTotMb)
}
Write-Output ""

# -- DISK --
Write-Output "-- DISK --"
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $sizeGb = [math]::Round($_.Size / 1GB, 1)
    $freeGb = [math]::Round($_.FreeSpace / 1GB, 1)
    $usedGb = [math]::Round(($_.Size - $_.FreeSpace) / 1GB, 1)
    $pct    = if ($_.Size) { [math]::Round(($_.Size - $_.FreeSpace) / $_.Size * 100, 0) } else { 0 }
    Write-Output ("> {0} — Size: {1} GB | Used: {2} GB ({3}%) | Free: {4} GB" -f $_.DeviceID, $sizeGb, $usedGb, $pct, $freeGb)
}
Write-Output ""

# -- TOP PROCESSES --
Write-Output "-- PROCESSES --"
$procs = Get-Process
Write-Output ("> Total: {0} processes" -f $procs.Count)

Write-Output "> Top CPU:"
$procs | Sort-Object CPU -Descending | Select-Object -First 5 | ForEach-Object {
    Write-Output ("  - PID {0,-6} {1,-20} {2,8:N1}s CPU" -f $_.Id, $_.ProcessName, $_.CPU)
}
Write-Output "> Top MEM:"
$procs | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 | ForEach-Object {
    $wsMb = [math]::Round($_.WorkingSet64 / 1MB, 0)
    Write-Output ("  - PID {0,-6} {1,-20} {2,6} MB" -f $_.Id, $_.ProcessName, $wsMb)
}

Write-Output ""
Write-Output "----------------------------------------"
Write-Output "  End of report"
Write-Output "----------------------------------------"
