# Private evidence registry

The raw screenshots and raw status-line payloads remain outside Git. SHA-256 values identify the exact originals used for review and for the allowlisted public derivatives; hashes alone are not public proof.

| Private original | SHA-256 | Public derivative | Treatment |
| --- | --- | --- | --- |
| `cli/r1/pre-prompt.raw.png` | `01f57e3f334893f296c85a7257eb248877ec20ace21bcae8fa599811f0e7a6ea` | not published | Withheld; contains account and local-path identifiers |
| `cli/r1/response.raw.png` | `bc41ae44ef18f5f4fcaab85355b617793aaa1124dcd2b9018c2ffd8d993e225a` | not published | Withheld; contains account and local-path identifiers |
| `cli/r1/usage-page1.raw.png` | `c14d344c3987b168d62c5acb7f9e25d12d92cf1c90c1664a9507a1716472bbff` | not published | Withheld; contains account email |
| `cli/r1/usage-full.raw.png` | `054bea86a16f27ff38504e65a4121b6c1f3e62cdc9f82bf6937891f9191027fd` | not published | Withheld; contains account email |
| `cli/r2/pre-prompt.raw.png` | `f894f4c8284c936cef0154f7865b9d11f700c0db4db50dececcfba743cdd47e4` | not published | Withheld; contains account and local-path identifiers |
| `cli/r2/response.raw.png` | `c84281c4af73a1d2500bbe02b20526f7920e37ee57fdc25f44026577e012d20c` | not published | Withheld; contains account and local-path identifiers |
| `cli/r2/usage-full.raw.png` | `5d57b5e81e0059a9520d5a1328442a202fe134682b9e1e6e2b9b4e79e66a7276` | not published | Withheld; contains account email |
| `cli/r3/pre-prompt.raw.png` | `128ec38945917066d605c57812f02b000b207bb8e8cae6cb5e2d1aecdf4f0812` | not published | Withheld; contains account and local-path identifiers |
| `cli/r3/response.raw.png` | `1b493e8dd914cb74ed5039979bc2ccdd864bd4d141e169dc3c26ada3918d3145` | `attempts/r3/response.png` | Byte-identical copy; no private identifier is visible |
| `cli/r3/usage-full.raw.png` | `aa8fa5aba0b8ec0489d871c3795984229b029b5d207c894b90aebab2d39881f9` | not published | Withheld; contains account email |
| `statusline-private/cli-r1.raw.jsonl` | `0f49b443a984590e5c860bda34213166a79c030a3855ef1860aac0bcaf8e20f6` | `attempts/r1/*.sanitized.jsonl` | Safe-field allowlist |
| `statusline-private/cli-r2.raw.jsonl` | `5c860c000c7513065ea407f13dc577facc570e8de5ef5b057b5f6eff1f6f5530` | `attempts/r2/*.sanitized.jsonl` | Safe-field allowlist |
| `statusline-private/cli-r3.raw.jsonl` | `1600a1728793544f8e31d7a0ccafaec357650022444a441ed83ed8c0c86eda0c` | `attempts/r3/*.sanitized.jsonl` | Safe-field allowlist |

The withheld originals contain an account email, local absolute paths, and session/conversation identifiers. No authentication credential is included in the public package. Public status-line snapshots were created by allowlisting fields rather than by publishing or editing the complete raw payload.
