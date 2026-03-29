"""
keygen.py - RSA Key Generation

Generates cryptographically appropriate RSA key pairs using large primes.
"""

import random
import math


def is_prime(n, k=20):
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits=1024):
    """Generate a random prime of the given bit length."""
    while True:
        # Generate a random odd number of the right size
        p = random.getrandbits(bits)
        p |= (1 << bits - 1)  # Ensure it's `bits` bits long
        p |= 1                 # Ensure it's odd
        if is_prime(p):
            return p


def mod_inverse(e, phi):
    """Extended Euclidean Algorithm to find modular inverse of e mod phi."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        return gcd, y1 - (b // a) * x1, x1

    gcd, x, _ = extended_gcd(e % phi, phi)
    if gcd != 1:
        raise ValueError("e and phi(n) are not coprime — cannot find modular inverse.")
    return x % phi


def generate_keypair(bits=1024):
    """
    Generate an RSA public/private key pair.

    Args:
        bits: Bit length of each prime (key size = 2*bits). Default 1024.

    Returns:
        Tuple of ((e, n), (d, n)) — (public_key, private_key)
    """
    print(f"[*] Generating {bits*2}-bit RSA key pair...")

    # Generate two distinct primes
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Common public exponent
    e = 65537
    if math.gcd(e, phi_n) != 1:
        raise ValueError("e=65537 is not coprime with phi(n). Try regenerating keys.")

    # Private exponent
    d = mod_inverse(e, phi_n)

    public_key = (e, n)
    private_key = (d, n)

    print(f"[+] Key generation complete.")
    print(f"    n  = {n}")
    print(f"    e  = {e}")
    print(f"    d  = {d}")

    return public_key, private_key


if __name__ == "__main__":
    pub, priv = generate_keypair(bits=512)  # 512-bit for quick demo; use 1024 in production
    print("\nPublic Key  (e, n):", pub)
    print("Private Key (d, n):", priv)
