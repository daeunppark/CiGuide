# Implementation Usage Table

|No.|Symmetric Encryption Scheme|Runtime Efficiency|Security|Freshness Check (ADDED)|Storage Complexity — Output (ADDED)|Time Complexity (ADDED)|Message Length Required in Advance (ADDED)|Integrated Authentication (ADDED)|Parallel Encryption (ADDED)|
|---|---|---|---|---|---|---|---|---|---|
|1|AES-CBC|Fast|Achieves IND-CPA security if AES is a secure PRP and IVs are unpredictable.|no|n + p + v bytes|O(n)|no|no|no|
|2|AES-CBC + HMAC-SHA256|Fast; slightly slower than No. 1|Achieves IND-CCA security if AES-CBC is IND-CPA secure and HMAC-SHA256 is strongly unforgeable, using independent keys and Encrypt-then-MAC.|no|n + p + v + t bytes|O(n)|no|no|no|
|3|AES-CBC + HMAC-SHA256 + Timestamping|Fast; slightly slower than No. 2|Achieves IND-CCA security if AES-CBC is IND-CPA secure and HMAC-SHA256 is strongly unforgeable, using independent keys and Encrypt-then-MAC. Adds authenticated timestamp freshness checking; full replay/order protection requires receiver policy and state.|yes|n + p + v + t + s bytes|O(n)|no|no|no|
|4 (ADDED)|AES-GCM|Fast; more parallelizable than No. 5|Achieves nonce-respecting IND-CCA security and ciphertext integrity if AES is a secure PRP, nonces are unique per key, and tag-length and usage limits are respected.|no|n + v + t bytes|O(n + a)|no|yes|yes|
|5 (ADDED)|AES-CCM|Fast; less parallelizable than No. 4 due to sequential CBC-MAC processing|Achieves nonce-respecting IND-CCA security and ciphertext integrity if AES is a secure PRP, nonces are unique per key, and tag-length and usage limits are respected.|no|n + v + t bytes|O(n + a)|yes|yes|no|

All lengths are bytes: n = plaintext, a = associated data, p = PKCS#7 padding (1–16), v = IV/nonce, t = authentication tag, s = timestamp. CBC IVs are 16 bytes; full HMAC-SHA256 tags are 32 bytes. Storage is output data plus explicitly stored metadata, excluding keys, AAD, protocol headers and replay state. Bounds assume linear processing and fixed-size key/tag/timestamp. Variable-length AAD also makes CBC+MAC O(n+a). Timestamp checking alone does not ensure complete replay protection or ordering.

See [Sources](sources.md).
