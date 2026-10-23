# Textbook RSA Toolkit: `rsa_encrypt.py` and `rsa_decrypt.py`

A pair of small, dependency-free Python command line tools that encrypt and decrypt data with **textbook RSA**. They are built for learning, coursework and demonstrations: every step is commented, every input is validated, and both tools can show their working.

> **Security warning:** This is *textbook* RSA with a tiny key (n = 1271). It is deterministic, unpadded and trivially breakable. **Do not use it to protect real data.** See [Security notes](#security-notes).

---

## Table of contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Files](#files)
4. [Quick start](#quick-start)
5. [How RSA works (short version)](#how-rsa-works-short-version)
6. [The default key](#the-default-key)
7. [`rsa_encrypt.py` reference](#rsa_encryptpy-reference)
8. [`rsa_decrypt.py` reference](#rsa_decryptpy-reference)
9. [Text encoding schemes](#text-encoding-schemes)
10. [Worked examples](#worked-examples)
11. [Using the code as a library](#using-the-code-as-a-library)
12. [Design notes: what changed from the original scripts](#design-notes-what-changed-from-the-original-scripts)
13. [Testing](#testing)
14. [Error messages and troubleshooting](#error-messages-and-troubleshooting)
15. [Security notes](#security-notes)
16. [Limitations](#limitations)

---

## Features

| Feature | `rsa_encrypt.py` | `rsa_decrypt.py` |
|---|:---:|:---:|
| Exact integer modular exponentiation (`pow(x, k, n)`) | yes | yes |
| Works on lists of numbers | yes | yes |
| Works on text (`ascii` or `alphabet` encoding) | `--text` | `--decode` |
| Input validation (`0 <= value < n`) | yes | yes |
| Does not modify the caller's list | yes | yes |
| Key validation (checks e is usable) | yes | n/a |
| Chinese Remainder Theorem (CRT) speed-up | n/a | yes (when n factors) |
| Recovers p, q, φ(n) and e from the key | checks only | yes |
| Step-by-step explanation (`--explain`) | yes | n/a |
| Round-trip verification against a private key | `--verify-d` | n/a |
| Warns about RSA fixed points (0 and 1) | yes | n/a |
| Built-in self-test over every possible message | `--selftest` | `--selftest` |

## Requirements

- **Python 3.8 or newer** (the decryptor uses `pow(a, -1, m)`, added in 3.8). Tested on Python 3.12.
- **No third-party packages.** Only the standard library is used.

## Files

```
rsa_encrypt.py   Encrypts numbers or text with a public key (n, e)
rsa_decrypt.py   Decrypts numbers (and optionally decodes to text) with a private key (n, d)
README.md        This file
```

## Quick start

```bash
# 1. Encrypt the word HELLO (A=1 ... Z=26)
python rsa_encrypt.py --text "HELLO" --scheme alphabet
#   Cipher   : [777, 800, 321, 321, 1170]

# 2. Decrypt it again and show it as text
python rsa_decrypt.py 777 800 321 321 1170 --decode alphabet
#   Plain    : [8, 5, 12, 12, 15]
#   Text     : HELLO
```

Run either script with `-h` for the full option list, or with no arguments for a small demo (`[1, 2]`).

---

## How RSA works (short version)

RSA is built from two keys that are mathematically linked.

**Key generation** (already done for you, see [the default key](#the-default-key)):

1. Pick two primes, `p` and `q`.
2. Compute the modulus `n = p × q`.
3. Compute `φ(n) = (p − 1)(q − 1)`.
4. Pick a public exponent `e` that shares no factor with `φ(n)`.
5. Compute the private exponent `d` so that `e × d ≡ 1 (mod φ(n))`.

**The keys:**

- Public key: `(n, e)`. Anyone may have it. Used by `rsa_encrypt.py`.
- Private key: `(n, d)`. Keep it secret. Used by `rsa_decrypt.py`.

**The operations:**

```
Encrypt:  c = m^e  mod n      (m = message number, 0 <= m < n)
Decrypt:  m = c^d  mod n      (c = ciphertext number, 0 <= c < n)
```

It works because `e × d ≡ 1 (mod φ(n))`, so raising to `e` and then to `d` gets you back to where you started (Euler's theorem).

---

## The default key

Both scripts ship with the same classroom key, so they work together out of the box.

| Value | Number | Meaning |
|---|---|---|
| `p` | 31 | first prime |
| `q` | 41 | second prime |
| `n` | 1271 | modulus = 31 × 41 |
| `φ(n)` | 1200 | (31 − 1)(41 − 1) |
| `e` | 17 | public exponent (coprime to 1200) |
| `d` | 353 | private exponent: 17 × 353 = 6001 = 5 × 1200 + 1 |

Because `n = 1271`, every message and ciphertext must be an integer from **0 to 1270**. Override the key with `--n`, `--e` and `--d` (see below).

---

## `rsa_encrypt.py` reference

```
python rsa_encrypt.py [numbers ...] [options]
```

### Input

| Argument | Description |
|---|---|
| `numbers` | One or more integers to encrypt. Each must satisfy `0 <= m < n`. |
| `--text TEXT` | Encrypt this text instead of numbers. |
| `--scheme {ascii,alphabet}` | How `--text` becomes numbers. Default: `ascii`. |

With no `numbers` and no `--text`, the script encrypts `[1, 2]` as a demo.

### Key options

| Option | Default | Description |
|---|---|---|
| `--n N` | 1271 | Modulus. |
| `--e E` | 17 | Public exponent. |

### Output and checking options

| Option | Description |
|---|---|
| `--explain` | Print the square-and-multiply steps for every message. |
| `--verify-d D` | Decrypt the result with private exponent `D` and confirm it matches the original. Exits with code 1 if it does not. |
| `--selftest` | Round-trip every message from 0 to n − 1 and exit. |
| `-h`, `--help` | Show help. |

### Output fields

```
Key      : n=1271, e=17
Text     : 'HELLO' (alphabet)          (only when --text is used)
Plain    : [8, 5, 12, 12, 15]          the numbers that were encrypted
Cipher   : [777, 800, 321, 321, 1170]  the encrypted numbers
Warning  : [1] encrypt to themselves   (only if 0 or 1 appears)
Verified : YES, ...                    (only with --verify-d)
```

### Key validation

When the key is created, the encryptor checks:

- `n >= 4`
- `3 <= e < n`
- If `n` is small enough to factor, that `gcd(e, φ(n)) == 1`. Otherwise no private key could ever exist.

For example, `--e 4` is rejected because 4 shares a factor with φ(n) = 1200.

---

## `rsa_decrypt.py` reference

```
python rsa_decrypt.py [ciphertext ...] [options]
```

### Input

| Argument | Description |
|---|---|
| `ciphertext` | One or more integers to decrypt. Each must satisfy `0 <= c < n`. |

With no ciphertext, the script decrypts `[1, 2]` as a demo.

### Options

| Option | Default | Description |
|---|---|---|
| `--n N` | 1271 | Modulus. |
| `--d D` | 353 | Private exponent. |
| `--decode {ascii,alphabet}` | none | Also show the plaintext numbers as text. |
| `--no-factor` | off | Skip factoring `n`. Use this for large moduli, where trial division would take forever. Decryption falls back to plain `pow(c, d, n)`. |
| `--selftest` | off | Encrypt then decrypt every message from 0 to n − 1 (with and without CRT) and exit. |
| `-h`, `--help` | | Show help. |

### Output fields

```
Key      : n=1271, d=353  (p=31, q=41, e=17)
Method   : CRT                      (or: plain modular exponentiation)
Cipher   : [...]                    what you gave it
Plain    : [...]                    decrypted numbers
Text     : HELLO                    (only with --decode)
```

### Decryption methods

- **Plain:** `m = pow(c, d, n)`. Used when `n` cannot be factored or `--no-factor` is set.
- **CRT (Chinese Remainder Theorem):** used automatically when `n` factors into `p × q`. Instead of one big exponentiation mod `n`, it does two smaller ones mod `p` and `q`, then combines them with Garner's formula:

  ```
  dp    = d mod (p − 1)
  dq    = d mod (q − 1)
  q_inv = q⁻¹ mod p
  m_p   = c^dp mod p
  m_q   = c^dq mod q
  h     = q_inv × (m_p − m_q) mod p
  m     = m_q + h × q
  ```

  This is how real RSA libraries decrypt, and it is roughly 3 to 4 times faster on large keys. Both methods give identical answers (the self-test proves it for this key).

---

## Text encoding schemes

RSA only understands numbers, so text must be converted first. Both tools share the same two schemes.

| Scheme | Mapping | Notes |
|---|---|---|
| `ascii` | Each character becomes its code point (`'A'` → 65, `'h'` → 104). | Works for any character whose code is below `n`. With `n = 1271`, that covers all of ASCII and a good part of Latin-1 and beyond. |
| `alphabet` | `A`..`Z` → 1..26, space → 0. Case-insensitive on input. | Letters and spaces only. Decoding shows `?` for anything outside 0 to 26. |

**Important:** use the same scheme to decode that you used to encode. If you decode `ascii`-encoded numbers with `alphabet`, you will see `?` characters.

---

## Worked examples

### 1. Encrypt and decrypt numbers

```bash
$ python rsa_encrypt.py 65 66 67
Key      : n=1271, e=17
Plain    : [65, 66, 67]
Cipher   : [363, 605, 552]
```

Feed the `Cipher` list into the decryptor (`python rsa_decrypt.py 363 605 552`) to get `[65, 66, 67]` back.

### 2. Encrypt text with ASCII and verify

```bash
$ python rsa_encrypt.py --text "Hi" --scheme ascii --verify-d 353
Key      : n=1271, e=17
Text     : 'Hi' (ascii)
Plain    : [72, 105]
Cipher   : [720, 414]
Verified : YES, decrypts back to the original

$ python rsa_decrypt.py 720 414 --decode ascii
Key      : n=1271, d=353  (p=31, q=41, e=17)
Method   : CRT
Cipher   : [720, 414]
Plain    : [72, 105]
Text     : Hi
```

### 3. See exactly how encryption works

```bash
$ python rsa_encrypt.py 5 --explain
Key      : n=1271, e=17
Plain    : [5]
Cipher   : [800]

How it works:
m = 5, e = 17 = 0b10001, n = 1271
  bit 0 = 1: square, multiply by m  -> 5
  bit 1 = 0: square                 -> 25
  bit 2 = 0: square                 -> 625
  bit 3 = 0: square                 -> 428
  bit 4 = 1: square, multiply by m  -> 800
  => ciphertext = 800
```

This is *square-and-multiply*. The binary form of `e` (10001) tells you what to do at each step: always square, and also multiply by `m` when the bit is 1. It takes about log₂(e) steps rather than `e` steps, and every intermediate value is reduced mod `n` so it never grows large.

### 4. Use your own key

Pick `p = 61`, `q = 53`: `n = 3233`, `φ = 3120`, `e = 17`, `d = 2753`.

```bash
$ python rsa_encrypt.py 65 --n 3233 --e 17 --verify-d 2753
Cipher   : [2790]
Verified : YES, decrypts back to the original

$ python rsa_decrypt.py 2790 --n 3233 --d 2753
Plain    : [65]
```

### 5. Large moduli

For a modulus too big to factor by trial division, skip the factoring step:

```bash
python rsa_decrypt.py 12345 --n <big n> --d <big d> --no-factor
```

### 6. Error handling

```bash
$ python rsa_encrypt.py 5000
Error: Message 5000 is out of range; need 0 <= m < 1271.

$ python rsa_decrypt.py 2000
Error: Ciphertext 2000 is out of range; need 0 <= c < 1271.

$ python rsa_encrypt.py --e 4
Error: e=4 shares a factor with phi(n)=1200; this key can't be decrypted. Choose a different e.
```

Errors go to `stderr` and the scripts exit with code 1, so they behave well in shell scripts.

---

## Using the code as a library

Both files can be imported.

```python
from rsa_encrypt import RSAPublicKey, encode_text
from rsa_decrypt import RSAPrivateKey, decode_numbers

pub = RSAPublicKey(n=1271, e=17)
priv = RSAPrivateKey.from_n_d(n=1271, d=353)   # factors n, enables CRT

numbers = encode_text("HELLO", "alphabet")      # [8, 5, 12, 12, 15]
cipher = pub.encrypt(numbers)                   # [777, 800, 321, 321, 1170]
plain = priv.decrypt(cipher)                    # [8, 5, 12, 12, 15]
print(decode_numbers(plain, "alphabet"))        # HELLO
```

### `rsa_encrypt.py` API

| Name | Description |
|---|---|
| `RSAPublicKey(n, e)` | Frozen dataclass. Validates the key on creation. |
| `.encrypt_int(m)` | Encrypt one integer. |
| `.encrypt(messages)` | Encrypt an iterable of integers. Returns a new list. |
| `.explain(m)` | Return the square-and-multiply trace as a list of strings. |
| `encode_text(text, scheme)` | Text to list of integers. |
| `verify_round_trip(key, d, messages, ciphertext)` | Returns `True` if decrypting with `d` recovers the messages. |
| `try_factor(n)` | Trial-division factoring for small `n`. Returns `(p, q)` or `None`. |
| `selftest()` | Exhaustive round-trip test. |

### `rsa_decrypt.py` API

| Name | Description |
|---|---|
| `RSAPrivateKey(n, d, p=None, q=None)` | Frozen dataclass. Uses CRT when `p` and `q` are given. |
| `RSAPrivateKey.from_n_d(n, d, factor=True)` | Build a key from `(n, d)`, factoring `n` if possible. |
| `.phi`, `.e` | Derived φ(n) and public exponent (when `p`, `q` are known). |
| `.decrypt_int(c)` | Decrypt one integer. |
| `.decrypt(ciphertext)` | Decrypt an iterable. Returns a new list. |
| `.encrypt_int(m)`, `.encrypt(plaintext)` | Encrypt using the derived `e` (handy for tests). |
| `decode_numbers(numbers, scheme)` | List of integers to text. |
| `factorize_semiprime(n)` | Split `n` into two distinct primes or raise `ValueError`. |
| `modular_inverse(a, m)` | `a⁻¹ mod m` or raise `ValueError`. |
| `selftest()` | Exhaustive round-trip test. |

---

## Design notes: what changed from the original scripts

The original scripts used `math.pow(x, k) % n`. That has three problems, all fixed here.

1. **Floating-point precision loss.** `math.pow` returns a float, which keeps only about 15 to 16 significant digits. `m^17` or `c^353` has far more digits, so the `% n` is computed on a rounded number. In the self-test, the old encryption method gave the **wrong ciphertext for 1234 of the 1271 possible messages**. Python's `pow(x, k, n)` works on exact integers and avoids this entirely.
2. **Needless work.** Building a number with hundreds of digits just to reduce it mod `n` is wasteful. Three-argument `pow` reduces at every step.
3. **Mutation of inputs.** The old functions overwrote the caller's list in place. The new ones return a fresh list.

On top of that fix, the rewrite adds input validation, key validation, CRT, text encoding, the `--explain` trace, round-trip verification, a CLI and self-tests.

---

## Testing

Run each built-in self-test:

```bash
python rsa_encrypt.py --selftest
python rsa_decrypt.py --selftest
```

Expected output:

```
# rsa_encrypt.py
Self-test: PASSED (all messages round-trip)
Old float method disagreed on 1234 of 1271 messages.

# rsa_decrypt.py
p=31, q=41, phi=1200, e=17
Self-test: PASSED (all messages round-trip)
```

What they check:

- **Encryptor:** for every `m` in 0..1270, `encrypt(m)` matches the exact reference `m**e % n`, and decrypting with `d = 353` returns `m`. It also counts how often the old float method was wrong.
- **Decryptor:** for every `m` in 0..1270, both the CRT path and the plain `pow` path return `m` after encryption.

Both scripts return exit code 0 on success and 1 on failure.

---

## Error messages and troubleshooting

| Message | Cause | Fix |
|---|---|---|
| `Message N is out of range; need 0 <= m < n` | A number to encrypt is negative or ≥ n. | Use smaller numbers, or a larger key. |
| `Ciphertext N is out of range; need 0 <= c < n` | A number to decrypt is negative or ≥ n. | Check you copied the full ciphertext and are using the right `--n`. |
| `e=E shares a factor with phi(n)` | Chosen `e` is not coprime to φ(n). | Pick another `e` (17, 65537 and other odd primes usually work). |
| `Character 'x' can't be encoded with 'alphabet'` | Digit or punctuation in alphabet mode. | Use `--scheme ascii`, or remove the character. |
| Decoded text shows `?` | Wrong decoding scheme, or the plaintext numbers aren't in range for it. | Decode with the same scheme you encoded with. |
| Decryption gives garbage numbers | Wrong `d`, or ciphertext came from a different key. | Make sure `n` and `d` match the key used to encrypt. Use `--verify-d` when encrypting. |
| `Verified : NO, d does not match this key` | The `--verify-d` value is not the inverse of `e` for this `n`. | Recompute `d = e⁻¹ mod φ(n)`. |
| Script seems to hang on a big key | Trial-division factoring of a large `n`. | Add `--no-factor` to the decryptor. |

---

## Security notes

This toolkit is educational. Several properties make textbook RSA unsafe for real use:

- **Tiny key.** `n = 1271` can be factored by hand in seconds. Real keys are 2048 bits or more (over 600 digits).
- **No padding.** Real RSA uses OAEP (or similar) to add randomness and structure. Without it, anyone can recognise patterns in the ciphertext. In the quick-start example, the two `L`s in HELLO both encrypt to `321`.
- **Deterministic.** The same message always gives the same ciphertext, so an attacker can guess a message, encrypt it with your public key and compare.
- **Fixed points.** `0` and `1` always encrypt to themselves.
- **Character-by-character encryption.** Encrypting each character separately is a simple substitution cipher in disguise: a frequency analysis attack can break it without ever touching RSA's maths.
- **Not constant-time.** Python integer maths leaks timing information.

For real applications, use a vetted library (for example `cryptography` in Python) with RSA-OAEP, or better, a modern hybrid scheme.

## Limitations

- Textbook RSA only: no padding, signatures or key generation.
- Messages are encoded one character per block, which is simple but insecure and inefficient.
- Factoring in both tools is trial division, so it is meant only for small educational keys.
- The `alphabet` scheme supports only the 26 English letters and space.
