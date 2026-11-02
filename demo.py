from offline_payments import OfflineClearingHouse, OfflineWallet, PaymentToken

token = PaymentToken.issue("wallet-demo", "token-001", 1200, expires_at=2000)
wallet = OfflineWallet("wallet-demo", [token], max_offline_value=5000)
accepted = wallet.spend("token-001", 350, "merchant-demo", now=1000)
replay = wallet.spend("token-001", 350, "merchant-demo", now=1001)
clearing = OfflineClearingHouse()
settlement = clearing.reconcile(accepted.receipt) if accepted.receipt else None
print({"mode": "simulation", "offline": accepted.reason, "replay": replay.reason, "settlement": settlement.reason if settlement else "none"})
