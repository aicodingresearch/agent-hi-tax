# Desktop measurement boundary

Google Antigravity 2.0 Desktop 2.11.0 exposes the selected model, effort, speed label, response text, rounded account-quota previews, and minute-level message timestamps in its official UI.

It does not expose an accepted official per-conversation interface for:

- input tokens;
- output or thinking tokens;
- context-total tokens;
- precise response latency; or
- an exact conversation-level quota charge.

The contributor confirmed that local application storage contains opaque SQLite and Protobuf data. Those fields are intentionally excluded: repository policy forbids reverse engineering a client to obtain measurements, and an interpretation produced by the product itself in conversation is not independent machine evidence.

Accordingly:

- all Desktop token fields are `not_exposed`;
- timing is `not_exposed` rather than inferred from equal minute labels;
- formal quota before/after is `not_measured`;
- rounded launch previews are retained only as launch/model evidence and have status `unverified_cache_state`;
- account-level quota attribution is `contaminated` because collection alternated with the paired CLI surface.

The paired CLI package independently reports product-native status-line fields. It must not be used to fill missing Desktop fields or to claim an exact cross-surface token delta.
