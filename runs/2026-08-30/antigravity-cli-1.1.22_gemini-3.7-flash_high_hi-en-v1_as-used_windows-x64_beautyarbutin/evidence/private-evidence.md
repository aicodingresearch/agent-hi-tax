# Private evidence registry

The raw screenshots and raw status-line payloads remain outside Git. SHA-256 values identify the exact originals used to create the public derivatives; hashes alone are not public proof.

| Private original | SHA-256 | Public derivative | Treatment |
| --- | --- | --- | --- |
| `r1-startup.raw.png` | `992338af37baae4ee33784a03ef28117aa582dd2270b3d1c6d318d6bc2c65488` | `evidence/environment.png` | Opaque rectangle over account email |
| `r2-startup.raw.png` | `ef0495f852c942f093d93eac8f62bbb9fb72c8ac240412ed75c87c623af5f778` | not published | Withheld as redundant scenario-level evidence |
| `r3-startup.raw.png` | `59a5d95b7a56d531a65f836f7032d85c29363a3200057faa0ec5cd747113d9cc` | not published | Withheld as redundant scenario-level evidence |
| `r1-response.raw.png` | `bac7ab9ba96e037003bb1d9d48b074d706977c1f0643bdeedf5a342f54ba7695` | `attempts/r1/response.png` | Byte-identical copy; no redaction needed |
| `r2-response.raw.png` | `ac58489cb3e0a4201331c51231b758308cbc875f9ae39a7bf0d4797614b434bc` | `attempts/r2/response.png` | Byte-identical copy; no redaction needed |
| `r3-response.raw.png` | `222cc1a396c8fef13e55630b8ef48c5168a6088fda8fe702015c3c647adf7e47` | `attempts/r3/response.png` | Byte-identical copy; no redaction needed |
| `r1-usage-header.raw.png` | `f6696e119a966408c058ec8da9ca642969a5fcd4e427520498a10b8821caad4f` | `attempts/r1/usage-header.png` | Opaque rectangle over account email |
| `r1-usage-body.raw.png` | `83e476ea63e48750fd153c03336ec906390b82886fd7bc761c7f578abdaa8f3e` | `attempts/r1/usage.png` | Opaque rectangle over account email |
| `r2-usage-full.raw.png` | `8aa4d6f6c08c4be4cf4cdf7ffbee9ea50d8bdf0fd6cc9031021995b50c905fa7` | `attempts/r2/usage.png` | Opaque rectangle over account email |
| `r3-usage-full.raw.png` | `c2fd675d869deaaa822ab39af78d72a4eb3b5b54949683f52f5448721be52852` | `attempts/r3/usage.png` | Opaque rectangle over account email |

The withheld originals contain an account email, local paths, and session/conversation identifiers. Raw status-line payloads remain privately retained but their hashes are not published; the review artifacts are the allowlisted public events. No authentication credential is included in the public package.
