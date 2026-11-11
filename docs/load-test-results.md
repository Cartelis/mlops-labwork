## Load Test Results

- Requests: 100 (sequential)
- P95 latency: 20.08 ms
- Average latency: 8.92 ms
- Throughput: 107.51 req/s

Atlikta naudojant load-test.ps1 failą.

> **Note:** Testas atliktas nuosekliai (1 request at a time) per
> `kubectl port-forward`. Throughput rodo tik vieno kliento pajėgumą
> per localhost — tai nėra produkcinio tinklo ar konkurencinio
> apkrovos matavimas.