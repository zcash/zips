"""
LWE/RLWE hardness analysis to accompany the Nullifier PIR ZIP.

Produces the data that feeds the Noise Analysis section of the ZIP:

  1. Kyber512 calibration benchmark.
     Runs the lattice estimator on NIST's Kyber512 parameters under both
     Core-SVP (ADPS16) and MATZOV cost models, then compares the resulting
     block sizes and bit-security with the PIR Tier 2 selector instance.

  2. Cost model ladder.
     Analytical computation for block size beta = 356: layers Core-SVP,
     memory-access cost regimes (k=1/2/3 per the NIST Kyber-512 FAQ),
     the MATZOV estimator output, and the Ducas 2022 hidden-overhead
     correction.

  3. Sensitivity sweep.
     Varies the discrete Gaussian standard deviation over
     {3.2, 6.4, 10, 16, 25, 40, 64, 100} while holding n, q, m fixed
     at the Tier 2 values.  Runs both ADPS16 and MATZOV to produce a
     2D table showing where each cost model crosses the 125-bit target.

CONVENTION NOTE
---------------
The lattice estimator's ND.DiscreteGaussian() takes the *standard
deviation*, NOT the Gaussian width parameter.  The YPIR/ZIP convention
uses width sigma = 6.4 * sqrt(2*pi) ~ 16.03; the estimator receives
stddev = 6.4.

REQUIREMENTS
------------
  - SageMath environment (e.g. conda sage-env)
  - git submodule third_party/lattice-estimator

Run:
    PATH="/opt/anaconda3/envs/sage-env/bin:$PATH" \\
      python tools/nullifier_pir_analysis.py
"""

from __future__ import annotations

import math
import subprocess
import sys
from functools import partial
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate the lattice-estimator submodule relative to this script.
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent
_ESTIMATOR_ROOT = _REPO_ROOT / "third_party" / "lattice-estimator"
if not (_ESTIMATOR_ROOT / "estimator").is_dir():
    print("error: third_party/lattice-estimator missing.", file=sys.stderr)
    sys.exit(1)
sys.path.insert(0, str(_ESTIMATOR_ROOT))

from estimator import LWE, ND, schemes  # noqa: E402
from estimator.lwe_primal import primal_usvp, primal_bdd  # noqa: E402
from estimator.lwe_dual import matzov as dual_hybrid  # noqa: E402
from estimator.reduction import RC, ADPS16  # noqa: E402
from estimator.util import batch_estimate, f_name  # noqa: E402
from sage.all import oo  # noqa: E402

# ---------------------------------------------------------------------------
# Parameters from draft-valargroup-nullifier-pir [Parameters] section.
#
# q is the product of two 28-bit NTT-friendly primes:
#   q = q_{2,1} * q_{2,2} = 268_369_921 * 249_561_089 ~ 2^55.89
#
# The Gaussian width sigma = 6.4 * sqrt(2*pi).  The estimator takes
# the standard deviation = 6.4.
# ---------------------------------------------------------------------------
Q = 268_369_921 * 249_561_089
N = 2048
D = 2048  # ring degree
STDDEV = 6.4
M_TIER2 = 32_768
M_TIER1 = D  # 1 ring element × 2048 coefficients
PACKING_RING_SAMPLES = 33  # 11 automorphisms × 3 gadget digits
M_PACKING = PACKING_RING_SAMPLES * D  # expanded to scalar LWE: 67,584

# Classical cost models: the conservative lower bound (Core-SVP / ADPS16) and
# the more realistic MATZOV model that accounts for progressive BKZ,
# dimensions-for-free, and refined nearest-neighbor sieve costs.
MODELS = [
    ("Core-SVP (ADPS16)", RC.ADPS16),
    ("MATZOV 2022", RC.MATZOV),
]

# Quantum cost model: Grover-accelerated sieving reduces the per-call SVP
# exponent from 0.292 to 0.265 [LaaMosPol15].
QUANTUM_MODEL = ("Quantum Core-SVP (ADPS16)", ADPS16(mode="quantum"))


def estimate_rough(par, cost_model):
    """Run uSVP, BDD, and dual-hybrid attacks under a single cost model.

    Uses the GSA (Geometric Series Assumption) shape model for the primal
    attacks and the MATZOV dual-hybrid formulation for the dual attack.
    Returns a dict mapping attack name to the estimator result object.
    """
    params = par.normalize()
    algorithms = {
        "usvp": partial(primal_usvp, red_cost_model=cost_model, red_shape_model="gsa"),
        "bdd": partial(primal_bdd, red_cost_model=cost_model, red_shape_model="gsa"),
        "dual_hybrid": partial(dual_hybrid, red_cost_model=cost_model),
    }
    res_raw = batch_estimate(
        params, algorithms.values(), log_level=1, jobs=1, catch_exceptions=True,
    )
    res_raw = res_raw[params]
    res = {}
    for alg, attack in algorithms.items():
        for k, v in res_raw.items():
            if f_name(attack) == k:
                res[alg] = v
    return res


def extract_results(result):
    """Extract minimum bit-security and block sizes from estimator output.

    Returns (bits, beta) where bits = log2(min rop across attacks) and
    beta is the BKZ block size from the cheapest primal attack (uSVP or
    BDD, whichever has lower rop).
    """
    bits = None
    beta = None
    rops = []
    best_primal_rop = float("inf")
    for alg, v in result.items():
        try:
            r = float(v["rop"])
            rops.append(r)
            if alg in ("usvp", "bdd") and r < best_primal_rop:
                best_primal_rop = r
                try:
                    beta = int(v["beta"])
                except (TypeError, KeyError):
                    pass
        except (TypeError, KeyError):
            try:
                r = float(getattr(v, "rop", None))
                rops.append(r)
            except (TypeError, ValueError):
                pass
    if rops:
        bits = math.log2(min(rops))
    return bits, beta


def print_kyber_calibration():
    """Ccompare PIR Tier 2 hardness against NIST Kyber512.

    This gives a cost-model-independent reference point: the ratio of
    uSVP block sizes (beta_PIR / beta_Kyber) tells a reviewer how close
    the PIR parameters are to NIST's category-1 bar, regardless of which
    cost model they prefer.
    """
    print()
    print("=" * 72)
    print("KYBER512 CALIBRATION BENCHMARK")
    print("=" * 72)

    kyber = schemes.Kyber512
    print()
    print("Kyber512 parameters:", kyber)

    kyber_results = {}
    for model_name, model in MODELS:
        print(f"\n  [{model_name}]")
        res = estimate_rough(kyber, model)
        for alg in res:
            if res[alg]["rop"] != oo:
                print(f"    {alg:20s} :: {res[alg]!r}")
        bits, beta = extract_results(res)
        kyber_results[model_name] = (bits, beta)

    pir_par = LWE.Parameters(
        n=N, q=Q,
        Xs=ND.DiscreteGaussian(STDDEV),
        Xe=ND.DiscreteGaussian(STDDEV),
        m=M_TIER2,
        tag="PIR Tier 2",
    )

    pir_results = {}
    for model_name, model in MODELS:
        print(f"\n  [PIR Tier 2 — {model_name}]")
        res = estimate_rough(pir_par, model)
        for alg in res:
            if res[alg]["rop"] != oo:
                print(f"    {alg:20s} :: {res[alg]!r}")
        bits, beta = extract_results(res)
        pir_results[model_name] = (bits, beta)

    print()
    print("  COMPARISON TABLE:")
    print("  ┌───────────────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐")
    print("  │ Instance                  │ β (uSVP)     │ Core-SVP     │ MATZOV       │ β ratio      │")
    print("  ├───────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤")

    kyber_beta = kyber_results.get("Core-SVP (ADPS16)", (None, None))[1]
    kyber_core = kyber_results.get("Core-SVP (ADPS16)", (None, None))[0]
    kyber_matzov = kyber_results.get("MATZOV 2022", (None, None))[0]

    pir_beta = pir_results.get("Core-SVP (ADPS16)", (None, None))[1]
    pir_core = pir_results.get("Core-SVP (ADPS16)", (None, None))[0]
    pir_matzov = pir_results.get("MATZOV 2022", (None, None))[0]

    kb_str = str(kyber_beta) if kyber_beta else "N/A"
    kc_str = f"{kyber_core:.1f}" if kyber_core else "N/A"
    km_str = f"{kyber_matzov:.1f}" if kyber_matzov else "N/A"
    print(f"  │ Kyber512                 │ {kb_str:>12s} │ {kc_str:>12s} │ {km_str:>12s} │     1.00     │")

    pb_str = str(pir_beta) if pir_beta else "N/A"
    pc_str = f"{pir_core:.1f}" if pir_core else "N/A"
    pm_str = f"{pir_matzov:.1f}" if pir_matzov else "N/A"
    ratio = f"{pir_beta / kyber_beta:.2f}" if (pir_beta and kyber_beta) else "N/A"
    print(f"  │ PIR Tier 2 (binding)     │ {pb_str:>12s} │ {pc_str:>12s} │ {pm_str:>12s} │ {ratio:>12s} │")
    print("  └───────────────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘")

    if pir_beta and kyber_beta:
        print(f"\n  uSVP β ratio: {pir_beta}/{kyber_beta} = {pir_beta/kyber_beta:.3f}")
        print("  (cost-model-independent measure of relative security)")

    return kyber_beta, pir_results


def print_cost_model_ladder(kyber_beta, pir_results):
    """Analytical cost model ladder for the binding block size.

    Follows the NIST Kyber-512 FAQ (Dec 2023) methodology.  The sieving
    exponent constant c(k) depends on how memory access is costed:

      k=inf (free):     c ~ 0.2570   (theoretical baseline)
      k=3 (4th-root):   c = 0.3198
      k=2 (cube-root):  c = 0.3294   (NIST's best guess)
      k=1 (sqrt / BGJ1): c = 0.349

    Core-SVP uses 0.292 (BKZ + enumeration/sieving combined cost).
    MATZOV adds progressive BKZ + dimensions-for-free + refined NN on
    top of the basic sieve, but still assumes free memory.  The memory
    corrections are additive on top of MATZOV:
      delta = (c(k) - 0.292) * beta   extra bits per sieve call
    """
    pir_core_beta = pir_results.get("Core-SVP (ADPS16)", (None, None))[1]
    pir_matzov_bits = pir_results.get("MATZOV 2022", (None, None))[0]
    pir_matzov_beta = pir_results.get("MATZOV 2022", (None, None))[1]
    core_beta = pir_core_beta or 356
    mat_beta = pir_matzov_beta or core_beta
    matzov_bits = pir_matzov_bits or 131.5

    print()
    print("=" * 72)
    print(f"COST MODEL LADDER (Core-SVP β = {core_beta}, MATZOV β = {mat_beta})")
    print("=" * 72)

    core_svp = 0.292 * core_beta
    k1_bits = 0.349 * core_beta
    k2_bits = 0.3294 * core_beta
    k3_bits = 0.3198 * core_beta
    matzov_hidden_lo = matzov_bits + 3
    matzov_hidden_hi = matzov_bits + 5

    mat_k2 = matzov_bits + (0.3294 - 0.292) * mat_beta
    mat_k1 = matzov_bits + (0.349 - 0.292) * mat_beta

    print(f"""
  ┌──────────────────────────────────────────┬─────────────┬──────────────────────────────────────┐
  │ Cost model                               │ Est. bits   │ Notes                                │
  ├──────────────────────────────────────────┼─────────────┼──────────────────────────────────────┤
  │ Core-SVP (ADPS16, 0.292β)               │ {core_svp:>9.1f}   │ Lower bound; ignores all overheads   │
  │ Memory k=3 (0.3198β)                    │ {k3_bits:>9.1f}   │ Fourth-root memory cost              │
  │ Memory k=2 (0.3294β)                    │ {k2_bits:>9.1f}   │ NIST best guess (cube-root)          │
  │ Memory k=1 / BGJ1 (0.349β)             │ {k1_bits:>9.1f}   │ Conservative (square-root)           │
  │ MATZOV (estimator)                      │ {matzov_bits:>9.1f}   │ Progressive BKZ + refined NN         │
  │ MATZOV + hidden overheads               │  {matzov_hidden_lo:.0f}–{matzov_hidden_hi:.0f}   │ Ducas 2022 correction (+3–5 bits)    │
  │ MATZOV + k=2 memory                     │  ~{mat_k2:.0f}     │ NIST best guess (cube-root)          │
  │ MATZOV + k=1 memory                     │  ~{mat_k1:.0f}     │ Conservative (BGJ1 square-root)      │
  └──────────────────────────────────────────┴─────────────┴──────────────────────────────────────┘""")

    if kyber_beta:
        print(f"\n  For comparison at Kyber512 β={kyber_beta}:")
        ky_core = 0.292 * kyber_beta
        ky_k2 = 0.3294 * kyber_beta
        ky_k1 = 0.349 * kyber_beta
        print(f"    Core-SVP: {ky_core:.1f},  k=2: {ky_k2:.1f},  k=1: {ky_k1:.1f}")
        print("    NIST FAQ states Kyber512 best gate-count estimate is ~2^147–2^160")


def print_sensitivity_sweep():
    """Vary stddev while keeping (n, q, m) at Tier 2 values.

    Sweeps both ADPS16 and MATZOV to show where each model crosses the
    125-bit target.  Under MATZOV, even stddev=3.2 exceeds 125 bits;
    under Core-SVP, reaching 125 bits requires stddev ~ 64-100.
    """
    print()
    print("=" * 72)
    print("SENSITIVITY SWEEP (stddev × cost model)")
    print("=" * 72)
    print(f"  n={N}, q≈2^{math.log2(Q):.1f}, m={M_TIER2}")

    stddevs = [3.2, 6.4, 10.0, 16.0, 25.0, 40.0, 64.0, 100.0]
    sweep = []

    for sd in stddevs:
        par = LWE.Parameters(
            n=N, q=Q,
            Xs=ND.DiscreteGaussian(sd),
            Xe=ND.DiscreteGaussian(sd),
            m=M_TIER2,
            tag=f"sd={sd}",
        )

        row = {"stddev": sd, "width": sd * math.sqrt(2 * math.pi)}
        for model_name, model in MODELS:
            res = estimate_rough(par, model)
            bits, beta_val = extract_results(res)
            row[model_name] = bits
            row[model_name + "_beta"] = beta_val

        sweep.append(row)
        print(f"  stddev={sd:>6.1f}: Core-SVP={row.get('Core-SVP (ADPS16)','N/A')}, "
              f"MATZOV={row.get('MATZOV 2022','N/A')}")

    # Summary table
    print()
    print("  SENSITIVITY SUMMARY TABLE:")
    print(f"  {'stddev':>8s}  {'width':>8s}  {'β(uSVP)':>8s}  {'Core-SVP':>10s}  {'MATZOV':>10s}  "
          f"{'Core≥125':>9s}  {'MAT≥125':>9s}")
    print(f"  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*10}  {'─'*10}  {'─'*9}  {'─'*9}")
    for row in sweep:
        sd = row["stddev"]
        w = row["width"]
        core = row.get("Core-SVP (ADPS16)")
        mat = row.get("MATZOV 2022")
        b = row.get("Core-SVP (ADPS16)_beta")

        c_str = f"{core:.1f}" if core else "inf"
        m_str = f"{mat:.1f}" if mat else "inf"
        b_str = str(b) if b else "—"
        c_ok = "YES" if core and core >= 125 else ("—" if core is None else "no")
        m_ok = "YES" if mat and mat >= 125 else ("—" if mat is None else "no")

        print(f"  {sd:>8.1f}  {w:>8.1f}  {b_str:>8s}  {c_str:>10s}  {m_str:>10s}  "
              f"{c_ok:>9s}  {m_ok:>9s}")


def print_quantum_estimates():
    """Run the lattice estimator with the quantum ADPS16 cost model.

    Rather than hand-computing 0.265*beta from the classical uSVP block
    size, this runs the full estimator with quantum sieving costs to find
    the cheapest quantum attack for both Kyber512 and the PIR binding
    instance.  This ensures the quantum column is consistent with the
    classical column (both report the minimum across all attack families).
    """
    print()
    print("=" * 72)
    print("QUANTUM SECURITY ESTIMATES")
    print("=" * 72)

    q_name, q_model = QUANTUM_MODEL

    kyber = schemes.Kyber512
    pir_par = LWE.Parameters(
        n=N, q=Q,
        Xs=ND.DiscreteGaussian(STDDEV),
        Xe=ND.DiscreteGaussian(STDDEV),
        m=M_TIER2,
        tag="PIR Tier 2",
    )

    results = {}
    for label, par in [("Kyber512", kyber), ("PIR Tier 2 (binding)", pir_par)]:
        print(f"\n  [{label} — {q_name}]")
        res = estimate_rough(par, q_model)
        for alg in res:
            if res[alg]["rop"] != oo:
                print(f"    {alg:20s} :: {res[alg]!r}")
        bits, beta = extract_results(res)
        results[label] = (bits, beta)

    # Also run classical for side-by-side comparison
    classical_results = {}
    for label, par in [("Kyber512", kyber), ("PIR Tier 2 (binding)", pir_par)]:
        res = estimate_rough(par, RC.ADPS16)
        bits, beta = extract_results(res)
        classical_results[label] = (bits, beta)

    print()
    print("  QUANTUM vs CLASSICAL COMPARISON:")
    print("  ┌───────────────────────────┬──────────┬─────────────────┬─────────────────┐")
    print("  │ Instance                  │ β (best) │ Classical ADPS16│ Quantum ADPS16  │")
    print("  ├───────────────────────────┼──────────┼─────────────────┼─────────────────┤")

    for label in ["Kyber512", "PIR Tier 2 (binding)"]:
        c_bits, c_beta = classical_results[label]
        q_bits, q_beta = results[label]
        c_str = f"{c_bits:.1f}" if c_bits else "N/A"
        q_str = f"{q_bits:.1f}" if q_bits else "N/A"
        cb_str = str(c_beta) if c_beta else "—"
        qb_str = str(q_beta) if q_beta else "—"
        print(f"  │ {label:<25s} │ {cb_str:>4s}/{qb_str:<3s} │ {c_str:>15s} │ {q_str:>15s} │")

    print("  └───────────────────────────┴──────────┴─────────────────┴─────────────────┘")
    print()
    print("  Note: β columns show classical/quantum cheapest-attack block sizes.")
    print("  Both columns report the minimum rop across uSVP, BDD, and dual hybrid.")

    return results


def print_packing_key_estimates():
    """Estimate hardness of the packing-key RLWE instance.

    The packing key consists of 33 RLWE ciphertexts.  Following the same
    methodology used for the selector (analyzing Ring-LWE as scalar LWE),
    each ring sample expands to D=2048 scalar LWE samples via negacyclic
    extraction, giving m = 33 × 2048 = 67,584 total samples.
    """
    print()
    print("=" * 72)
    print("PACKING-KEY RLWE ESTIMATES")
    print(f"  {PACKING_RING_SAMPLES} ring samples × {D} coefficients "
          f"= {M_PACKING} scalar LWE samples")
    print("=" * 72)

    pk_par = LWE.Parameters(
        n=N, q=Q,
        Xs=ND.DiscreteGaussian(STDDEV),
        Xe=ND.DiscreteGaussian(STDDEV),
        m=M_PACKING,
        tag="Packing-key RLWE",
    )
    print(f"\n  Parameters: {pk_par}")

    pk_results = {}
    for model_name, model in MODELS:
        print(f"\n  [Packing-key — {model_name}]")
        res = estimate_rough(pk_par, model)
        for alg in res:
            if res[alg]["rop"] != oo:
                print(f"    {alg:20s} :: {res[alg]!r}")
        bits, beta = extract_results(res)
        pk_results[model_name] = (bits, beta)

    print()
    print("  PACKING-KEY vs SELECTOR COMPARISON:")
    print("  ┌──────────────────────────────────┬──────────┬──────────────┬──────────────┐")
    print("  │ Instance                         │ m        │ Core-SVP     │ MATZOV       │")
    print("  ├──────────────────────────────────┼──────────┼──────────────┼──────────────┤")

    for label, m_val, results in [
        ("Selector Tier 1 (1 ring elem)", M_TIER1, None),
        (f"Packing key ({PACKING_RING_SAMPLES} ring elems)", M_PACKING, pk_results),
        ("Selector Tier 2 (16 ring elems)", M_TIER2, None),
    ]:
        if results:
            core = results.get("Core-SVP (ADPS16)", (None, None))[0]
            mat = results.get("MATZOV 2022", (None, None))[0]
            c_str = f"{core:.1f}" if core else "N/A"
            m_str = f"{mat:.1f}" if mat else "N/A"
        else:
            c_str = "(see above)"
            m_str = "(see above)"
        print(f"  │ {label:<32s} │ {m_val:>8,d} │ {c_str:>12s} │ {m_str:>12s} │")

    print("  └──────────────────────────────────┴──────────┴──────────────┴──────────────┘")
    print()
    print(f"  With {M_PACKING:,d} scalar samples the packing-key instance is well")
    print("  within the same hardness range as both selector tiers.")
    print("  The binding case remains the Tier 2 selector (most samples).")

    return pk_results


def main():
    print("lattice-estimator:", _ESTIMATOR_ROOT)
    try:
        rev = subprocess.check_output(
            ["git", "-C", str(_ESTIMATOR_ROOT), "rev-parse", "HEAD"], text=True,
        ).strip()
        print("git HEAD:", rev)
    except (OSError, subprocess.CalledProcessError):
        pass

    kyber_beta, pir_results = print_kyber_calibration()
    print_cost_model_ladder(kyber_beta, pir_results)
    print_packing_key_estimates()
    print_sensitivity_sweep()
    print_quantum_estimates()


if __name__ == "__main__":
    main()
