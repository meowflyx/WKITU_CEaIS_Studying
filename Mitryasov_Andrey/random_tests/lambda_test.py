containers = [
    {"name": "nginx-proxy", "status": "running", "cpu_percent": 2.5, "ram_mb": 150},
    {"name": "postgres-db", "status": "running", "cpu_percent": 45.2, "ram_mb": 1024},
    {"name": "redis-cache", "status": "exited", "cpu_percent": 0.0, "ram_mb": 0},
    {"name": "python-backend", "status": "running", "cpu_percent": 88.5, "ram_mb": 512},
    {"name": "grafana", "status": "restarting", "cpu_percent": 12.0, "ram_mb": 200}
]

# решение в несколько строк

running_containers = filter((lambda x: x["status"] == "running"), containers)

running_containers_sorted_by_load = sorted(running_containers, key=lambda s: s["cpu_percent"], reverse=True)

print(running_containers_sorted_by_load)

# решение в одну строку

print(sorted(filter(lambda x: x["status"] == "running", containers), key=lambda s: s["cpu_percent"], reverse=True))

