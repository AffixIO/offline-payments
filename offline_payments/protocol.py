from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

def digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

@dataclass(frozen=True)
class PaymentToken:
    token_id: str
    wallet_id: str
    currency: str
    value: int
    expires_at: int
    nullifier: str
    issuer_evidence: str

    @classmethod
    def issue(cls, wallet_id: str, token_id: str, value: int, expires_at: int, currency: str = "GBP"):
        if value <= 0: raise ValueError("token value must be positive")
        body = {"token_id": token_id, "wallet_id": wallet_id, "currency": currency, "value": value, "expires_at": expires_at}
        return cls(token_id, wallet_id, currency, value, expires_at, digest({"token": token_id, "wallet": wallet_id}), digest(body))

@dataclass(frozen=True)
class SpendResult:
    accepted: bool
    reason: str
    receipt: dict | None = None

@dataclass(frozen=True)
class Settlement:
    receipt_id: str
    token_id: str
    nullifier: str
    value: int
    currency: str
    merchant_id: str
    evidence_digest: str

class OfflineWallet:
    """Local simulation of a wallet holding pre-authorised offline tokens."""
    def __init__(self, wallet_id: str, tokens: Iterable[PaymentToken] = (), max_offline_value: int = 5000):
        self.wallet_id = wallet_id
        self.tokens = {token.token_id: token for token in tokens}
        self.spent_nullifiers: set[str] = set()
        self.max_offline_value = max_offline_value

    def spend(self, token_id: str, amount: int, merchant_id: str, now: int) -> SpendResult:
        token = self.tokens.get(token_id)
        if not token: return SpendResult(False, "unknown-token")
        if token.wallet_id != self.wallet_id: return SpendResult(False, "wrong-wallet")
        if token.nullifier in self.spent_nullifiers: return SpendResult(False, "double-spend")
        if now >= token.expires_at: return SpendResult(False, "expired")
        if amount <= 0 or amount > token.value: return SpendResult(False, "amount-out-of-range")
        if amount > self.max_offline_value: return SpendResult(False, "offline-limit")
        self.spent_nullifiers.add(token.nullifier)
        receipt = {"receipt_id": digest({"token": token_id, "merchant": merchant_id, "now": now})[:24], "token_id": token_id, "nullifier": token.nullifier, "value": amount, "currency": token.currency, "merchant_id": merchant_id, "wallet_id": self.wallet_id}
        receipt["evidence_digest"] = digest(receipt)
        return SpendResult(True, "accepted-offline", receipt)

    def reconcile(self, receipts: Iterable[dict]) -> list[Settlement]:
        settlements = []
        for receipt in receipts:
            if receipt.get("nullifier") not in self.spent_nullifiers: continue
            settlements.append(Settlement(receipt["receipt_id"], receipt["token_id"], receipt["nullifier"], receipt["value"], receipt["currency"], receipt["merchant_id"], receipt["evidence_digest"]))
        return settlements
