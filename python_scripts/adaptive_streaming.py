import requests
import math
import time

BASE_URL = "http://localhost:2011/meta"


def get_all_configs():
    resp = requests.get(f"{BASE_URL}/get_all_configs")
    return eval(resp.text)["configs"]


def set_config(config_str):
    requests.post(f"{BASE_URL}/set_config", json={"config": config_str})


def get_perception():
    resp = requests.get(f"{BASE_URL}/get_perception")
    try:
        data = eval(resp.text.replace("false", "False"))
    except Exception:
        return None
    return data


def choose_ucb(stats, total):
    best_cfg = None
    best_val = float('-inf')
    for cfg, s in stats.items():
        if s["count"] == 0:
            val = float('inf')
        else:
            avg = s["reward"] / s["count"]
            val = avg + math.sqrt((2 * math.log(max(total,1))) / s["count"])
        if val > best_val:
            best_val = val
            best_cfg = cfg
    return best_cfg


def main(rounds=50, wait_time=5):
    configs = get_all_configs()
    if not configs:
        print("No configurations returned by server")
        return
    stats = {cfg: {"count": 0, "reward": 0.0} for cfg in configs}
    total = 0

    for i in range(rounds):
        cfg = choose_ucb(stats, total)
        print(f"[Round {i+1}] selecting config: {cfg}")
        set_config(cfg)
        time.sleep(wait_time)
        perception = get_perception()
        metric = None
        if perception and perception.get("metrics"):
            metric = perception["metrics"][0].get("metric")
        if metric is None:
            metric = 0
        reward = -metric  # lower metric is better
        stats[cfg]["count"] += 1
        stats[cfg]["reward"] += reward
        total += 1
        print(f"  metric={metric}")

    best_cfg = max(stats.keys(), key=lambda c: stats[c]["reward"] / stats[c]["count"] if stats[c]["count"] else float('-inf'))
    print(f"Best configuration found: {best_cfg}")


if __name__ == "__main__":
    main()
