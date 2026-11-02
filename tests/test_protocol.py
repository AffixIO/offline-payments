import pytest
from offline_payments import OfflineClearingHouse, OfflineWallet, PaymentToken

def wallet():
    token = PaymentToken.issue("w-1", "t-1", 1000, 100)
    return OfflineWallet("w-1", [token], max_offline_value=1000)

def test_accepts_once_and_rejects_nullifier_replay():
    w = wallet(); first = w.spend("t-1", 250, "m-1", 50)
    assert first.accepted
    assert w.spend("t-1", 250, "m-2", 51).reason == "double-spend"

def test_fail_closed_for_expiry_amount_wallet_and_unknown_token():
    w = wallet()
    assert w.spend("missing", 1, "m", 1).reason == "unknown-token"
    assert w.spend("t-1", 1, "m", 100).reason == "expired"
    assert w.spend("t-1", 0, "m", 1).reason == "amount-out-of-range"
    assert OfflineWallet("other", w.tokens.values()).spend("t-1", 1, "m", 1).reason == "wrong-wallet"

def test_offline_limit_and_reconciliation():
    token = PaymentToken.issue("w", "t", 1000, 99)
    w = OfflineWallet("w", [token], max_offline_value=100)
    assert w.spend("t", 101, "m", 1).reason == "offline-limit"
    result = w.spend("t", 100, "m", 1)
    assert len(w.reconcile([result.receipt])) == 1

def test_token_values_must_be_positive():
    with pytest.raises(ValueError): PaymentToken.issue("w", "t", 0, 1)

def test_connected_reconciliation_catches_duplicate_receipts_globally():
    token = PaymentToken.issue("w", "t-global", 100, 99)
    first_wallet = OfflineWallet("w", [token]); second_wallet = OfflineWallet("w", [token])
    first = first_wallet.spend("t-global", 50, "m-1", 1).receipt
    second = second_wallet.spend("t-global", 50, "m-2", 2).receipt
    clearing = OfflineClearingHouse()
    assert clearing.reconcile(first).reason == "settled"
    assert clearing.reconcile(second).reason == "global-double-spend"

def test_reconciliation_rejects_altered_receipt():
    token = PaymentToken.issue("w", "t-altered", 100, 99)
    receipt = OfflineWallet("w", [token]).spend("t-altered", 50, "m", 1).receipt
    receipt["value"] = 99
    assert OfflineClearingHouse().reconcile(receipt).reason == "tampered-receipt"
