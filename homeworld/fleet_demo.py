"""python fleet_demo.py — the headless self-test (NT Part 6).

This is the project's regression suite: it recomputes the Bible's
worked examples through the REAL referee and simulation and prints
PASS/FAIL for human eyes. After ANY change to fleet or referee, this
must still print 12/12.
"""

import sys
import time
import traceback

import numpy as np

import referee
from sim import FleetSim
from orders import MoveCombination, Trim

_RESULTS = []


def check(label, ok):
    _RESULTS.append(bool(ok))
    print(f"{label} {'PASS' if ok else 'FAIL'}")


def close(a, b, tol=1e-9):
    return np.allclose(np.asarray(a, float), np.asarray(b, float), atol=tol)


def same_direction(v, w, tol=1e-9):
    v = np.asarray(v, float); w = np.asarray(w, float)
    v = v / np.linalg.norm(v); w = w / np.linalg.norm(w)
    return abs(abs(v @ w) - 1.0) < tol


def _det_sim(seed):
    sim = FleetSim(seed)
    ids = [sim.spawn("fighter", (2.0 * i, 0.0, 0.0), squad=1)
           for i in range(3)]
    sim.submit(MoveCombination(squad=1, coeffs=(3.0, 2.0, 1.0),
                               diagonal=True))
    for k in range(100):
        if k % 10 == 0:
            sim.submit(Trim(ids[0], (1.0, 0.0, 0.0)))
        sim.tick(0.1)
    return np.concatenate([sim.ships[i].pos for i in ids])


def main():
    print("FLEET SELF-TEST — referee + simulation core")

    A = np.array([[2.0, 1.0, 3.0], [0.0, 3.0, 3.0]])
    check(" 1. rank of the 2x3 matrix with columns (2,0),(1,3),(3,3) == 2 .......",
          referee.rank(A) == 2)

    C, R, kept = referee.cr_factor(A)
    check(" 2. cr_factor keeps columns [0,1] and R's third column == (1,1) ......",
          kept == [0, 1] and close(R[:, 2], [1.0, 1.0], 1e-8))

    Ag = np.array([[2.0, 1.0], [0.0, 3.0]])
    x_hat, e, en = referee.least_squares(Ag, np.array([7.0, 6.0]))
    check(" 3. shield solve: A columns (2,0),(1,3), b=(7,6) -> x=(2.5,2.0) ......",
          close(x_hat, [2.5, 2.0], 1e-8) and en < 1e-8)

    N = referee.nullspace_basis(np.array([[1.0, 1.0, 0.0],
                                          [0.0, 1.0, 1.0]]))
    check(" 4. nullspace of rows (1,1,0),(0,1,1) is spanned by +-(1,-1,1)/sqrt3 .",
          N.shape == (3, 1) and same_direction(N[:, 0], [1.0, -1.0, 1.0], 1e-8))

    N2 = referee.nullspace_basis(np.array([[1.0, 1.0, 0.0]]))
    check(" 5. jamming row 2 grows nullspace dimension 1 -> 2 ...................",
          N.shape[1] == 1 and N2.shape[1] == 2)

    Als = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
    x_hat, e, en = referee.least_squares(Als, np.array([6.0, 0.0, 0.0]))
    check(" 6. least squares pings (0,6),(1,0),(2,0) -> (C,D)=(5,-3) ............",
          close(x_hat, [5.0, -3.0], 1e-8))

    V = np.column_stack([[2.0, 0.0, 0.0], [0.0, 3.0, 0.0], [1.0, 1.0, 1.0]])
    check(" 7. det of columns (2,0,0),(0,3,0),(1,1,1) == 6 ......................",
          abs(referee.spanned_volume(V) - 6.0) < 1e-9)

    S = np.array([[0.8, 0.3], [0.2, 0.7]])
    w, Vec = np.linalg.eig(S)
    dom = Vec[:, int(np.argmax(w.real))].real
    check(" 8. swarm matrix [[0.8,0.3],[0.2,0.7]] dominant eigenvector ~ (3,2) ..",
          same_direction(dom, [3.0, 2.0], 1e-8))

    v, lam = referee.weak_axis(np.array([[5.0, 4.0], [4.0, 5.0]]))
    check(" 9. weak axis of [[5,4],[4,5]] is +-(1,-1)/sqrt2, eigenvalue 1 .......",
          abs(lam - 1.0) < 1e-9 and same_direction(v, [1.0, -1.0], 1e-8))

    rng = np.random.default_rng(7)
    G = rng.random((16, 16))
    energies = [referee.svd_partial(G, k)[1] for k in range(1, 17)]
    monotone = all(energies[i] <= energies[i + 1] + 1e-12
                   for i in range(15))
    check("10. svd_partial: energy fraction increases with k, reaches 1.0 .......",
          monotone and abs(energies[-1] - 1.0) < 1e-9)

    check("11. determinism: two sims, same seed+orders, identical after 100 ticks",
          np.array_equal(_det_sim(1234), _det_sim(1234)))

    sim = FleetSim(42)
    for i in range(20):
        sim.spawn("fighter", (float(i), 0.0, 0.0), squad=1)
    sim.submit(MoveCombination(squad=1, coeffs=(5.0, 3.0, 2.0),
                               diagonal=False))
    t0 = time.perf_counter()
    for _ in range(100):
        sim.tick(0.1)
    elapsed = time.perf_counter() - t0
    check("12. 100 pulses with 20 ships in < 0.5 s (performance floor) ..........",
          elapsed < 0.5)

    passed = sum(_RESULTS)
    total = len(_RESULTS)
    if passed == total:
        print(f"FLEET SELF-TEST PASSED ({passed}/{total})")
    else:
        print(f"FLEET SELF-TEST FAILED ({passed}/{total})")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        text = traceback.format_exc()
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("fleet.demo crash\n")
            f.write(text)
        print("Something broke — please copy crashlog.txt to the team.")
        print(text)
        sys.exit(1)
