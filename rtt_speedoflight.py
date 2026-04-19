"""
RTT vs. Speed-of-Light
Networks Assignment — Measurement & Geography

Run with: python rtt_speedoflight.py   (no sudo needed)
Requires: pip install requests matplotlib numpy
"""

import math, time, os, requests, numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import urllib.request

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

TARGETS = {
    "Tokyo":        {"url": "http://www.google.co.jp",   "coords": (35.6762,  139.6503), "continent": "Asia"},
    "São Paulo":    {"url": "http://www.google.com.br",  "coords": (-23.5505, -46.6333), "continent": "S. America"},
    "Lagos":        {"url": "http://www.google.com.ng",  "coords": (6.5244,     3.3792), "continent": "Africa"},
    "Frankfurt":    {"url": "http://www.google.de",      "coords": (50.1109,    8.6821), "continent": "Europe"},
    "Sydney":       {"url": "http://www.google.com.au",  "coords": (-33.8688, 151.2093), "continent": "Oceania"},
    "Mumbai":       {"url": "http://www.google.co.in",   "coords": (19.0760,   72.8777), "continent": "Asia"},
    "London":       {"url": "http://www.google.co.uk",   "coords": (51.5074,   -0.1278), "continent": "Europe"},
    "Singapore":    {"url": "http://www.google.com.sg",  "coords": (1.3521,   103.8198), "continent": "Asia"},
}

PROBES           = 15
FIBER_SPEED_KM_S = 200_000
FIGURES_DIR      = "figures"

CONTINENT_COLORS = {
    "Asia":      "#e63946",
    "S. America":"#2a9d8f",
    "Africa":    "#e9c46a",
    "Europe":    "#457b9d",
    "Oceania":   "#a8dadc",
}

# ─────────────────────────────────────────────
# TASK 1 — MEASURE RTTs
# ─────────────────────────────────────────────

def measure_rtt(url: str, probes: int = PROBES) -> dict:
    """
    Measure RTT to `url` using HTTP requests.
    """
    samples = []
    lost    = 0

    for _ in range(probes):
        try:
            start = time.perf_counter()
            with urllib.request.urlopen(url, timeout=3) as response:
                response.read(1)
            elapsed_ms = (time.perf_counter() - start) * 1000
            samples.append(elapsed_ms)
        except Exception:
            lost += 1
        time.sleep(0.2)

    if not samples:
        return {
            "min_ms": None,
            "mean_ms": None,
            "median_ms": None,
            "loss_pct": 100.0,
            "samples": []
        }

    return {
        "min_ms": float(np.min(samples)),
        "mean_ms": float(np.mean(samples)),
        "median_ms": float(np.median(samples)),
        "loss_pct": (lost / probes) * 100,
        "samples": samples,
    }


# ─────────────────────────────────────────────
# TASK 2 — HAVERSINE + INEFFICIENCY
# ─────────────────────────────────────────────

def great_circle_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute great-circle distance in km using the Haversine formula.
    """
    R = 6371

    lat1_r = math.radians(lat1)
    lon1_r = math.radians(lon1)
    lat2_r = math.radians(lat2)
    lon2_r = math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_my_location() -> tuple[float, float, str]:
    """Return (lat, lon, city) for this machine's public IP."""
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5).json()
        lat, lon = map(float, r["loc"].split(","))
        return lat, lon, r.get("city", "Your Location")
    except Exception:
        print("Could not auto-detect location. Defaulting to Boston.")
        return 42.3601, -71.0589, "Boston"


def compute_inefficiency(results: dict, src_lat: float, src_lon: float) -> dict:
    """
    Annotate each city in results with distance, theoretical minimum RTT,
    inefficiency ratio, and high inefficiency flag.
    """
    for city, data in results.items():
        dst_lat, dst_lon = data["coords"]
        distance_km = great_circle_km(src_lat, src_lon, dst_lat, dst_lon)
        theoretical_min_ms = 2 * (distance_km / FIBER_SPEED_KM_S) * 1000

        median_ms = data.get("median_ms")
        ratio = None if median_ms is None else median_ms / theoretical_min_ms

        data["distance_km"] = distance_km
        data["theoretical_min_ms"] = theoretical_min_ms
        data["inefficiency_ratio"] = ratio
        data["high_inefficiency"] = (ratio is not None and ratio > 3.0)

    return results


# ─────────────────────────────────────────────
# TASK 3 — PLOTS
# ─────────────────────────────────────────────

def make_plots(results: dict):
    """
    Produce two figures saved to FIGURES_DIR/.
    """
    os.makedirs(FIGURES_DIR, exist_ok=True)
    valid  = {c: d for c, d in results.items() if d.get("median_ms") is not None}
    cities = sorted(valid, key=lambda c: valid[c]["distance_km"])

    if not cities:
        print("No valid RTT samples available; skipping plots.")
        return

    # ── Figure 1 ──────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(cities))
    width = 0.38
    measured = [valid[c]["median_ms"] for c in cities]
    theoretical = [valid[c]["theoretical_min_ms"] for c in cities]

    ax.bar(x - width / 2, measured, width=width, label="Measured median RTT")
    ax.bar(x + width / 2, theoretical, width=width, label="Theoretical minimum RTT")
    ax.set_xticks(x)
    ax.set_xticklabels(cities, rotation=30, ha="right")
    ax.set_ylabel("RTT (ms)")
    ax.set_xlabel("City")
    ax.set_title("Measured RTT vs. Theoretical Fiber Minimum")
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/fig1_rtt_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()

    # ── Figure 2 ──────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 7))
    distances = [valid[c]["distance_km"] for c in cities]
    medians = [valid[c]["median_ms"] for c in cities]

    for city in cities:
        d = valid[city]
        color = CONTINENT_COLORS.get(d["continent"], "gray")
        ax.scatter(d["distance_km"], d["median_ms"], color=color, s=70)
        ax.text(d["distance_km"] + 120, d["median_ms"] + 2, city, fontsize=9)

    xline = np.linspace(0, max(distances) * 1.05, 200)
    yline = 2 * (xline / FIBER_SPEED_KM_S) * 1000
    ax.plot(xline, yline, linestyle="--", label="Theoretical minimum")

    legend_handles = [
        mpatches.Patch(color=color, label=continent)
        for continent, color in CONTINENT_COLORS.items()
        if any(valid[c]["continent"] == continent for c in cities)
    ]
    legend_handles.append(plt.Line2D([0], [0], linestyle="--", color="black", label="Theoretical minimum"))

    ax.set_xlabel("Great-circle distance (km)")
    ax.set_ylabel("Measured median RTT (ms)")
    ax.set_title("Distance vs. Measured RTT")
    ax.legend(handles=legend_handles)
    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/fig2_distance_scatter.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Figures saved to {FIGURES_DIR}/")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    src_lat, src_lon, src_city = get_my_location()
    print(f"Your location: {src_city} ({src_lat:.4f}, {src_lon:.4f})\n")

    results = {}
    for city, info in TARGETS.items():
        print(f"Probing {city} ({info['url']}) ...", end=" ", flush=True)
        stats = measure_rtt(info["url"])
        results[city] = {**stats, "coords": info["coords"], "continent": info["continent"]}
        med = stats.get("median_ms")
        print(f"median={med:.1f} ms  loss={stats['loss_pct']:.0f}%" if med else "unreachable")

    results = compute_inefficiency(results, src_lat, src_lon)

    print(f"\n{'City':<14} {'Dist km':>8} {'Median ms':>10} {'Theor. ms':>10} {'Ratio':>7}")
    print("─" * 55)
    for city, d in sorted(results.items(), key=lambda x: x[1].get("distance_km", 0)):
        dist  = d.get("distance_km", 0)
        med   = d.get("median_ms")
        theor = d.get("theoretical_min_ms")
        ratio = d.get("inefficiency_ratio")
        flag  = " ⚠️" if d.get("high_inefficiency") else ""
        print(f"{city:<14} {dist:>8.0f} "
              f"{(f'{med:.1f}' if med else 'N/A'):>10} "
              f"{(f'{theor:.1f}' if theor else 'N/A'):>10} "
              f"{(f'{ratio:.2f}' if ratio else 'N/A'):>7}{flag}")

    make_plots(results)

if __name__ == "__main__":
    main()
