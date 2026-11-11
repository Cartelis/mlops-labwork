$uri = "http://localhost:8000/predict"

$body = @{
    year = 2020
    mileage = 50000
} | ConvertTo-Json

# 5 apšilimo užklausos (į rezultatą neįtraukiamos)
Write-Host "Vykdomos apšilimo uzklausos..."

1..5 | ForEach-Object {
    Invoke-RestMethod -Uri $uri -Method Post `
        -ContentType "application/json" -Body $body | Out-Null
}

# 100 matuojamų užklausų
$latencies = [System.Collections.Generic.List[double]]::new()
$totalTimer = [System.Diagnostics.Stopwatch]::StartNew()

Write-Host "Vykdomos 100 uzklausu..."

1..100 | ForEach-Object {
    $timer = [System.Diagnostics.Stopwatch]::StartNew()

    Invoke-RestMethod -Uri $uri -Method Post `
        -ContentType "application/json" -Body $body | Out-Null

    $timer.Stop()
    $latencies.Add($timer.Elapsed.TotalMilliseconds)
}

$totalTimer.Stop()

# Rezultatu skaiciavimas
$sorted = @($latencies | Sort-Object)
$p95Index = [math]::Ceiling(0.95 * $sorted.Count) - 1
$p95 = $sorted[$p95Index]
$average = ($latencies | Measure-Object -Average).Average
$throughput = 100 / $totalTimer.Elapsed.TotalSeconds

Write-Host "`n===== LOAD TEST RESULTS ====="
Write-Host "Requests: 100"
Write-Host "Total time: $([math]::Round($totalTimer.Elapsed.TotalSeconds, 3)) s"
Write-Host "Average latency: $([math]::Round($average, 2)) ms"
Write-Host "P95 latency: $([math]::Round($p95, 2)) ms"
Write-Host "Throughput: $([math]::Round($throughput, 2)) requests/sec"