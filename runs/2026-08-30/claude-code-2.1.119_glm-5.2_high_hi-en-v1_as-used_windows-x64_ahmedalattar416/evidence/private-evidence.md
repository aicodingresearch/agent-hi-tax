# Private evidence registry

The raw screenshots remain outside Git. SHA-256 values allow the contributor to identify the exact private originals used to make the public derivatives.

| Private original | SHA-256 | Public derivative | Treatment |
| --- | --- | --- | --- |
| `environment.raw.png` | `c48fcd1352f2274d6bb5f68ed537e58d7c7d060dc74977f6010bde712f3a1847` | `environment.redacted.png` | Opaque rectangle over username (laptop-5v3drgl6\asus). Available original is a QQ-transferred resampled copy (1709x555, RGB); the pixel-exact pre-redaction 1575x501 source is lost. |
| `status.raw.png` | `c48fcd1352f2274d6bb5f68ed537e58d7c7d060dc74977f6010bde712f3a1847` | `status.redacted.png` | Opaque rectangles over Session ID and auth token. Same QQ-transferred original as environment (shared source screenshot). Pixel-exact pre-redaction source lost. |
| `r1-response.raw.png` | `155b91b3e369775cfe7c0f0e1a5d7e865d30cc3f5515476627a2cad5e9f588f2` | `attempts/r1/response.png` | Byte-identical copy; no redaction needed |
| `r2-response.raw.png` | `63d6f1cf4e48d2bee15cb3b515a8ec2729263a4f577ecdda4eb6419be2e0aa40` | `attempts/r2/response.png` | Byte-identical copy; no redaction needed |
| `r3-response.raw.png` | `e0de3468241dad328c2d380792f0322407990329e6dd7e3f8d02c3eb05fb87d9` | `attempts/r3/response.png` | Byte-identical copy; no redaction needed |

The private originals contain a local username, home path, Session IDs, or redundant copies of those fields. They are intentionally withheld. No authentication token or credential was captured in the published evidence. Usage data was extracted from transcript JSONL files, not from screenshots.
