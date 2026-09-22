# Origin

Folder encrypt / decrypt CLI — AES-256-GCM with a password-derived key
(PBKDF2-HMAC-SHA256, 480 000 iterations) via
[cryptography](https://cryptography.io/en/latest/).

Archive format (`.fcr`, version 1): magic `FCR1` + version + iteration count +
salt + nonce + ciphertext.

No upstream skill tree. Password and optional folder path live in the
per-workspace `.env` (`FOLDER`, `PASSWORD`) or are prompted / passed as CLI args.
