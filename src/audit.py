from datetime import datetime, timedelta
from enums import AuditLevel, RiskLevel


class AuditLog:
    def __init__(self, file_path: str = "audit.log"):
        self.file_path = file_path
        self.logs = []

    def log_event(self, level: AuditLevel, message: str):
        timestamp = datetime.now()

        record = {
            "time": timestamp,
            "level": level,
            "message": message
        }

        self.logs.append(record)

        log_line = f"[{timestamp}] [{level.value.upper()}] {message}\n"

        with open(self.file_path, "a", encoding="utf-8") as file:
            file.write(log_line)

    def filter_logs(self, level: AuditLevel):
        return [log for log in self.logs if log["level"] == level]

    def get_all_logs(self):
        return self.logs




class RiskAnalyzer:
    def __init__(self):
        self.transaction_history = []
        self.known_receivers = {}

    def analyze_transaction(self, transaction):
        risk_score = 0
        reasons = []


        if transaction.amount >= 5000:
            risk_score += 2
            reasons.append("Крупная сумма транзакции")


        current_hour = datetime.now().hour
        if 0 <= current_hour < 5:
            risk_score += 2
            reasons.append("Операция выполнена ночью")

        recent_transactions = [
            tx for tx in self.transaction_history
            if tx.sender
               and transaction.sender
               and tx.sender.account_id == transaction.sender.account_id
               and datetime.now() - tx.created_at <= timedelta(minutes=5)
        ]

        if len(recent_transactions) >= 3:
            risk_score += 2
            reasons.append("Слишком частые операции за короткое время")


        sender_id = transaction.sender.account_id if transaction.sender else None
        receiver_id = transaction.receiver.account_id if transaction.receiver else None

        if sender_id is not None and receiver_id is not None:
            if sender_id not in self.known_receivers:
                self.known_receivers[sender_id] = set()

            if receiver_id not in self.known_receivers[sender_id]:
                risk_score += 1
                reasons.append("Перевод на новый счет")
                self.known_receivers[sender_id].add(receiver_id)

        # Level
        if risk_score >= 5:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        self.transaction_history.append(transaction)

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reasons": reasons
        }