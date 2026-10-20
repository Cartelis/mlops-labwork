# Docker vaizdų dydžiai

MB = 1 000 000 baitų. Rootfs: išpakuotų failų dydis (`du --apparent-size`). Docker `.Size` priklauso nuo image store; containerd atveju tai suspausto turinio dydis, todėl jo nepainioti su rootfs ar bendra disko vieta.

| Vaizdas          | Platforma   | Docker .Size MB | Rootfs MB |
|------------------|-------------|----------------:|----------:|
| mlops-prepare:u1 | linux/amd64 | 1017.5          | 616       |
