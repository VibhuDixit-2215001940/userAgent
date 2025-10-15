import platform, psutil, requests, time

SERVER = "*******************" 

while True:
    data = {
    "hostname": platform.node(),
    "system": platform.system(),
    "os_version": platform.version(),
    "cpu_usage": psutil.cpu_percent(),
    "cpu_cores": psutil.cpu_count(logical=True),
    "memory_usage": psutil.virtual_memory().percent,
    "total_memory": psutil.virtual_memory().total,
    "disk_usage": psutil.disk_usage('/').percent,
    "uptime_sec": time.time() - psutil.boot_time()
    }
    try:
        r = requests.post(SERVER, json=data, timeout=10)
        # print("Status:", r.status_code, "| Response:", r.text)
        print("Gaya abb toh tu!")
    except Exception as e:
        print("Error:", e)
    time.sleep(30)
