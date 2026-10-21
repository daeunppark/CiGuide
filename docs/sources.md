References

# Sources

## Project basis

**NYU CS6903/4783 — Project 1.3.** CiGuide helps non-experts choose private-key encryption configurations using an extended lecture table, adaptive questions and a random-target correctness experiment.

## Lecture slides

These are page positions in the user-provided PDFs, rather than internal lecture labels.

- **f21-cs6903-lecture5.pdf:** p. 28 — CBC; p. 30 — CTR and parallel processing.
- **f21-cs6903-lecture6.pdf:** p. 19 — HMAC; p. 24 — Encrypt-then-MAC; pp. 25–26 — timestamping; p. 27 — the original comparison table.

## Added rows and columns

- **AES-GCM:** [NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final) — authenticated encryption, nonce limits, parallel and online processing; Appendix D covers replay limitations. [GCM security analysis (CRYPTO 2016)](https://www.iacr.org/archive/crypto2016/98140241/98140241.pdf) supports the PRP-based security explanation.
- **AES-CCM:** [NIST SP 800-38C](https://csrc.nist.gov/pubs/sp/800/38/c/upd1/final) and [RFC 3610 §6](https://www.rfc-editor.org/rfc/rfc3610.html#section-6) — CTR with CBC-MAC, sequential authentication and advance message-length requirements.
- **Freshness Check:** Lecture 6, pp. 25–27. Timestamp checking alone does not prevent every replay.
- **Storage and Time Complexity:** project-derived analytic expressions based on the constructions above. Padding follows [RFC 5652 §6.3](https://www.rfc-editor.org/rfc/rfc5652.html#section-6.3); SHA-256/HMAC details follow [RFC 6234](https://www.rfc-editor.org/rfc/rfc6234.html).
- **Message Length, Integrated Authentication and Parallel Encryption:** derived from CBC/HMAC and the GCM/CCM specifications above; CBC/CTR details also appear in [NIST SP 800-38A](https://csrc.nist.gov/pubs/sp/800/38/a/final).

## Project choices and limits

Rows 1–3 adapt the lecture by choosing CBC, HMAC-SHA256 and PKCS#7 padding. Storage formulas count output data and listed metadata, not working memory. Time formulas are analytic, not measured speeds. Questions, IDK examples and preference ranking are project designs.

Choice correctness counts a trial as successful when the target appears anywhere in the result list; it does not guarantee a unique answer. Storage budgets remain unassessed. A finished slide deck and presentation recording are still required.
