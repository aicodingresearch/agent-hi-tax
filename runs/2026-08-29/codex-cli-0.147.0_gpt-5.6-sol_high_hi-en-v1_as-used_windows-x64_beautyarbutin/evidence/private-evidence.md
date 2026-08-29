# Private evidence register

Raw terminal screenshots remain outside Git when they contain an account identifier, Session ID, resume command, or local absolute path. Public copies preserve the retained pixels and use deterministic cropping only; no image content is regenerated.

| Private artifact | SHA-256 | Public handling |
| --- | --- | --- |
| r1/status.raw.png | `3541caa52813ad02d63f3a746e5ca38269a52322c82caaf78a5d282892abe160` | Withheld: account identifier, Session ID, and local absolute path |
| r1/response.raw.png | `db0c9927684d26d45d3046bdf4b53bd70261ff90f638df5a4526a70feff28600` | Published as `attempts/r1/response.png`, cropped from 1239x389 to the top 1239x326 pixels to remove the local absolute path; no scaling or redrawing |
| r1/usage.raw.png | `1c44bda9190d36ab12e1edf50ea9501f1be0e6a8cf7203bc2d4df89de125949e` | Withheld: account identifier, Session ID, resume command, and local absolute path; token values are published in the sanitized event log |
| r2/status.raw.png | `891d015eae249968090a3f52f2543719cd9a2682ba3acdc4d02fe38abe7807dd` | Withheld: account identifier, Session ID, quota values, and local absolute path |
| r2/response.raw.png | `891d015eae249968090a3f52f2543719cd9a2682ba3acdc4d02fe38abe7807dd` | Identical duplicate of `r2/status.raw.png`; withheld and not used as response evidence |
| r2/usage.raw.png | `4841998a607b592ce77bd2d0135664b53d3d74f0f9b4ae074b917df46ff1df77` | Published as `attempts/r2/response.png`, cropped at `(x=0, y=570, width=1000, height=234)` from the 1734x927 original; the crop retains the prompt, transport warning, full response, and Token usage while excluding the resume command, Session ID, account identifier, and local path |
| r3/status.raw.png | `b15f4013aa376115a1bf8d0e52a9d27fc379513562dd5d271d6d408df61f4259` | Withheld: account identifier, Session ID, quota values, and local absolute path |
| r3/response.raw.png | `95355ac714fbc2ca18f5f0a1bd46c74486e63134605caaedc16f8f8c1b4275ce` | Published as `attempts/r3/response.png`, cropped at `(x=0, y=0, width=1151, height=190)` from the 1151x421 original to retain the prompt, transport warning, and full response while excluding the local absolute path |
| r3/usage.raw.png | `3fac7e583a645460e1bc19ef2010271f072742decba7a878fc155fec3d219e63` | Published as `attempts/r3/usage.png`, cropped at `(x=0, y=0, width=1160, height=38)` from the 1160x121 original to retain only the complete Token usage line and exclude the resume command, Session ID, and local absolute path |
