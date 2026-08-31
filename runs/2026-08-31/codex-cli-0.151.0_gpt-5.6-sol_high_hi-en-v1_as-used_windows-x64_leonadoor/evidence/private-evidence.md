# Private evidence registry

Raw screenshots and rollouts remain outside Git. These SHA-256 values identify the exact private originals used to produce the public derivatives; the hashes are an inventory aid, not public proof of the withheld contents.

| Private original | SHA-256 | Public derivative | Treatment |
| --- | --- | --- | --- |
| `r1/status.png` | `92d429c4d48e4098b2d56633b108d2e986ee50dc96f8fa967e1b377b4af4847c` | `environment.redacted.png` | Crop plus opaque account-email and Session-ID masks |
| `r2/status.png` | `a0faf692878e227d9faa69fb5de3d7c7b1b5ddb325954ea8216e152b62feff09` | not published | Withheld as redundant scene-level status evidence |
| `r3/status.png` | `73ade98218aecb46ec0fd6fbaa1353d6d3c0fc7f81a01e80f4e694c3faa66feb` | not published | Withheld as redundant scene-level status evidence |
| `plan.raw.png` | `82e523e99708dc8715cde9af88fddd7d79be3bd27d643d4c1c1eb8d792251dab` | `plan.png` | Crop retaining only the current Plus plan card |
| `r1/response.raw.png` | `db8fb1bc44bf0973bc611fc99650d2096edca589e27c8e9e55b5ac63b7dab6f3` | `attempts/r1/response.png` | Crop retaining exact input, transport warning, and complete reply |
| `r2/response.raw.png` | `22635b60bc4e902d894cd2d885eff0f25c03ae976e51407e4740e436663af4f0` | `attempts/r2/response.png` | Crop retaining exact input, transport warning, and complete reply |
| `r3/response.raw.png` | `70a9a8961b4c582f7c63484e788c6a616dd329086e511cc2acd47fc401071ea2` | `attempts/r3/response.png` | Crop retaining exact input, transport warning, and complete reply |
| `r1/usage.raw.png` | `12f6d46fa71ce73ce1ac6edc039ec84a2d0d6dc7c5d5c2bdc1bc882997be2808` | `attempts/r1/usage.png` | Crop retaining only the complete Token usage line |
| `r2/usage.raw.png` | `9f416f5743e78e3379cb115577cd2f302a7e2a0c6b0183cd7816b217f026a3ea` | `attempts/r2/usage.png` | Crop retaining only the complete Token usage line |
| `r3/usage.raw.png` | `5b49ba79a7185996ec62a65628590a7d79520e27112f1e4211b6474bc6c9d358` | `attempts/r3/usage.png` | Crop retaining only the complete Token usage line |
| `r1/rollout.private.jsonl` | `ced16fa0e04716ece1252d6a5338f890bed12845bdd6a39a8f9e282ce1480076` | `attempts/r1/events.sanitized.jsonl` | Minimal event extraction; identifiers, instructions, paths, and unrelated fields omitted |
| `r2/rollout.private.jsonl` | `1fa539400cf792696dae4f2b3a0503f9438247066ca937f0310dae6b7920ac88` | `attempts/r2/events.sanitized.jsonl` | Minimal event extraction; identifiers, instructions, paths, and unrelated fields omitted |
| `r3/rollout.private.jsonl` | `dc5e6e8fa362368edfc8c840a5f592f7ed38a556475e183e4bb9a002a4000725` | `attempts/r3/events.sanitized.jsonl` | Minimal event extraction; identifiers, instructions, paths, and unrelated fields omitted |

The private originals contain an account email, Session IDs, continuation identifiers, local paths, or full injected instructions. They are intentionally withheld. No authentication token or credential is present in the public evidence.
