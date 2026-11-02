# Offline payments with nullifiers

How can a device authorise a small payment when the network is unavailable, without pretending that offline data is the same thing as final settlement?

This repository is a dependency-light, simulated protocol for that boundary. A connected issuer creates a bounded payment token. A wallet can spend it offline once, using a nullifier to prevent replay. When connectivity returns, a clearing registry reconciles the receipt and applies global nullifier uniqueness.

## Five-minute quickstart

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install pytest
pytest -q
python demo.py
```

The demo accepts a fictional £3.50 offline spend, rejects a replay, then reconciles the receipt through a simulated clearing registry.

## Protocol boundary

```text
connected issuer
  → bounded token with expiry and nullifier
  → local merchant or wallet checks token offline
  → nullifier is consumed exactly once
  → receipt is retained locally
  → reconnect and reconcile
```

## Resilience use cases

The pattern is intended for continuity of essential services during short-lived connectivity loss: community shops, transport concessions, fuel or food distribution, field teams, temporary shelters, and local government service points. It can also support a controlled grace period for a business whose network link is down.

This is not a recommendation to hold less emergency cash, food or other supplies. Offline authorisation is a narrow technical fallback, not a substitute for resilient infrastructure, emergency planning or public guidance.

The nullifier prevents the same token from being accepted twice by the same wallet instance. A production system would also need a carefully designed issuer registry, device protection, merchant coordination, conflict handling, recovery, key rotation, rate limits and an explicit policy for what happens when two disconnected devices see related value.

The `OfflineClearingHouse` demonstrates the next boundary: two isolated wallet instances can each accept a copy of the same fictional token, but the first receipt reconciled online consumes the nullifier and the second is rejected as a global double-spend. This is why offline acceptance must be bounded and why reconciliation is authoritative.

## Threat model

The demo covers replay, expiry, wallet binding, amount limits, altered receipts and duplicate reconciliation. It does not solve stolen devices, compromised issuer keys, colluding merchants, forged hardware, unavailable revocation data, large-scale partitioned networks or legal settlement finality. Those require independent security review and operational controls.

## What AffixIO can verify

AffixIO can provide the evidence and policy layer around token issuance, spend scope, expiry, revocation and reconciliation decisions. The example keeps that boundary local and does not invent SDK methods. A production adapter should use only the documented AffixIO SDK interfaces for proof generation and verification, with signer pinning and no private keys in the repository.

## Safety and limitations

This is simulation code only. It does not connect to banks, cards, wallets, payment networks, stablecoins, merchants, live APIs or real funds. It is not a payment processor, stored-value wallet, banking product or financial advice.

Offline acceptance is not final settlement. It is a bounded authorisation decision that must be reconciled later. Real deployment would require security review, device attestation, regulatory analysis, issuer liability rules, privacy controls, double-spend analysis across devices, and independent cryptographic review.

## Status

Research example. Fictional data only.

## Contributing

Small tested improvements are welcome. Keep fixtures fictional and never commit credentials, private keys, payment data or personal information.

## License

MIT
