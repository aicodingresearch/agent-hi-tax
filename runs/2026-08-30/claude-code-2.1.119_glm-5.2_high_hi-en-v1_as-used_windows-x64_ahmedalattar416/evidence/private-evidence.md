# Private evidence registry

The raw screenshots remain outside Git. SHA-256 values allow the contributor to identify the exact private originals used to make the public derivatives.

| Private original | SHA-256 | Public derivative | Treatment |
| --- | --- | --- | --- |
| `environment.raw.png` | `C233BC6848C8AD56778DE0B9E55EF57CA0BCF533539D94EFEC83E9748E17908F` | `environment.redacted.png` | Opaque rectangle over username (laptop-5v3drgl6\asus) |
| `status.raw.png` | `B59AE930CF33B556FB84F5A75150CD2814FA5260B2CE76A550BDBE4F550A536E` | `status.redacted.png` | Opaque rectangles over Session ID and auth token |
| `r1-response.raw.png` | `155B91B3E369775CFE7C0F0E1A5D7E865D30CC3F5515476627A2CAD5E9F588F2` | `attempts/r1/response.png` | Byte-identical copy; no redaction needed |
| `r2-response.raw.png` | `63D6F1CF4E48D2BEE15CB3B515A8EC2729263A4F577ECDDA4EB6419BE2E0AA40` | `attempts/r2/response.png` | Byte-identical copy; no redaction needed |
| `r3-response.raw.png` | `E0DE3468241DAD328C2D380792F0322407990329E6DD7E3F8D02C3EB05FB87D9` | `attempts/r3/response.png` | Byte-identical copy; no redaction needed |

The private originals contain a local username, home path, Session IDs, or redundant copies of those fields. They are intentionally withheld. No authentication token or credential was captured in the published evidence. Usage data was extracted from transcript JSONL files, not from screenshots.