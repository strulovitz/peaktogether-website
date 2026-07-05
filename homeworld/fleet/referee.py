"""THE REFEREE (NEW_TESTAMENT 3.6) — canonical verdict functions.

This file is the mathematical conscience of the game (Bible Iron
Rule 4: NumPy is the Referee). Every module that needs a structural
verdict imports THESE functions; nobody reimplements them. All
signatures are frozen (INTERFACES v1.0).

Tolerance doctrine: structural verdicts never use equality.
"""

import numpy as np

TOL_RANK = 1e-6        # relative, on singular values
TOL_RESIDUAL = 1e-4    # absolute; missions may override per-context
TOL_IMAG = 1e-9


def rank(A):
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    s = np.linalg.svd(A, compute_uv=False)
    if s.size == 0 or s[0] <= 0.0:
        return 0
    return int(np.sum(s > TOL_RANK * s[0]))


def is_solvable(A, b):
    """b is reachable iff appending it as a column does not raise the
    rank, i.e. b lies in C(A). (Strang Ch. 2/3.)"""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    b = np.asarray(b, dtype=np.float64).reshape(-1, 1)
    return rank(A) == rank(np.column_stack([A, b]))


def residual(A, x, b):
    A = np.asarray(A, dtype=np.float64)
    x = np.asarray(x, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    return float(np.linalg.norm(A @ x - b))


def least_squares(A, b):
    """Returns (x_hat, error_vector, error_norm). (Strang 4.2-4.3.)"""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    b = np.asarray(b, dtype=np.float64)
    x_hat, *_ = np.linalg.lstsq(A, b, rcond=None)
    e = b - A @ x_hat
    return x_hat, e, float(np.linalg.norm(e))


def nullspace_basis(A):
    """Columns span N(A); empty (n, 0) array if the nullspace is {0}.
    From the SVD A = U S V^T: right singular vectors v_{r+1}..v_n
    satisfy A v_i = 0. (Strang 3.2.)"""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    _, _, Vt = np.linalg.svd(A)
    r = rank(A)
    return Vt[r:].T


def in_nullspace(A, x, eps):
    """(is_inside, level) where level = ||A x|| feeds the alarm meter."""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    x = np.asarray(x, dtype=np.float64)
    level = float(np.linalg.norm(A @ x))
    return level < eps, level


def spanned_volume(V):
    """V is 3x3 (three column vectors) -> |det|; 3x2 -> parallelogram
    area via the cross product. (Strang Ch. 5.)"""
    V = np.atleast_2d(np.asarray(V, dtype=np.float64))
    if V.shape[1] == 3:
        return float(abs(np.linalg.det(V)))
    return float(np.linalg.norm(np.cross(V[:, 0], V[:, 1])))


def real_eigen_axis(T):
    """The real eigenvector (eigenvalue nearest 1) of a rotation-like
    3D matrix T — the docking axis (Bible 2.11)."""
    T = np.asarray(T, dtype=np.float64)
    w, V = np.linalg.eig(T)
    i = int(np.argmin(np.abs(w.imag) + np.abs(w.real - 1.0)))
    v = V[:, i].real
    return v / np.linalg.norm(v)


def weak_axis(S):
    """Symmetric S -> (unit eigenvector of the smallest eigenvalue,
    that eigenvalue). (Strang 6.3-6.4.)"""
    S = np.asarray(S, dtype=np.float64)
    w, Q = np.linalg.eigh(S)
    return Q[:, 0], float(w[0])


def gram_penalty(Q):
    """How far the columns of Q are from orthonormal: ||Q^T Q - I||_F^2.
    (Strang 4.4.)"""
    Q = np.atleast_2d(np.asarray(Q, dtype=np.float64))
    G = Q.T @ Q
    return float(np.sum((G - np.eye(G.shape[1])) ** 2))


def cr_factor(A):
    """A = C R by greedy independent-column selection using rank();
    returns (C, R, kept_indices). R is solved per column by least
    squares on C. Exact for book-sized fleets. (Strang 1.4.)"""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    kept = []
    for j in range(A.shape[1]):
        if rank(A[:, kept + [j]]) > len(kept):
            kept.append(j)
    C = A[:, kept].copy()
    R = np.zeros((len(kept), A.shape[1]))
    for j in range(A.shape[1]):
        x, *_ = np.linalg.lstsq(C, A[:, j], rcond=None)
        R[:, j] = x
    return C, R, kept


def svd_partial(G, k):
    """Rank-k image and captured energy fraction (the Guidestone,
    Bible 2.14): G_k = U_k S_k Vt_k; energy = sum(s_i^2, i<=k) / sum."""
    G = np.atleast_2d(np.asarray(G, dtype=np.float64))
    U, s, Vt = np.linalg.svd(G, full_matrices=False)
    k = max(1, min(int(k), s.size))
    G_k = (U[:, :k] * s[:k]) @ Vt[:k]
    total = float(np.sum(s ** 2))
    energy = float(np.sum(s[:k] ** 2) / total) if total > 0.0 else 1.0
    return G_k, energy
