import json
import csv
import os
import matplotlib.pyplot as plt

from bank_system import Bank
from transactions import TransactionProcessor
from audit import AuditLog, RiskAnalyzer
from enums import TransactionStatus, RiskLevel


class ReportBuilder:
    def __init__(
            self,
            bank: Bank,
            processor: TransactionProcessor,
            risk_analyzer: RiskAnalyzer,
            audit_log: AuditLog,
            processed_transactions: list
    ):
        self.bank = bank
        self.processor = processor
        self.risk_analyzer = risk_analyzer
        self.audit_log = audit_log
        self.processed_transactions = processed_transactions

        self.output_dir = "reports_output"
        self.charts_dir = os.path.join(self.output_dir, "charts")

        self._prepare_directories()

    def _prepare_directories(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.charts_dir, exist_ok=True)

    def _get_client_accounts(self, client):
        return self.bank.search_accounts(client.client_id)

    def _get_client_account_ids(self, client):
        accounts = self._get_client_accounts(client)
        return {account.account_id for account in accounts}

    def _transaction_belongs_to_client(self, transaction, client_account_ids):
        sender_match = (
            transaction.sender is not None
            and transaction.sender.account_id in client_account_ids
        )

        receiver_match = (
            transaction.receiver is not None
            and transaction.receiver.account_id in client_account_ids
        )

        return sender_match or receiver_match

    def build_client_report(self, client):
        accounts = self._get_client_accounts(client)
        client_account_ids = {account.account_id for account in accounts}
        total_balance = sum(account._balance for account in accounts)

        client_transactions = []
        suspicious_operations = []

        for transaction in self.processed_transactions:
            if self._transaction_belongs_to_client(transaction, client_account_ids):
                client_transactions.append(transaction)

        for item in self.risk_analyzer.get_suspicious_operations_report():
            transaction = item["transaction"]

            if self._transaction_belongs_to_client(transaction, client_account_ids):
                suspicious_operations.append(
                    {
                        "transaction_id": transaction.transaction_id,
                        "risk_level": item["risk_level"].value,
                        "risk_score": item["risk_score"],
                        "reasons": item["reasons"],
                    }
                )

        completed_transactions = sum(
            1 for transaction in client_transactions
            if transaction.status == TransactionStatus.COMPLETED
        )

        failed_transactions = sum(
            1 for transaction in client_transactions
            if transaction.status == TransactionStatus.FAILED
        )

        report = {
            "client_name": client.full_name,
            "client_id": client.client_id,
            "accounts_count": len(accounts),
            "total_balance": total_balance,
            "transactions": {
                "total": len(client_transactions),
                "completed": completed_transactions,
                "failed": failed_transactions,
            },
            "accounts": [
                {
                    "account_id": account.account_id,
                    "currency": account.currency.value,
                    "balance": account._balance,
                    "status": account.status.value,
                }
                for account in accounts
            ],
            "suspicious_operations_count": len(suspicious_operations),
            "suspicious_operations": suspicious_operations,
        }

        return report

    def build_bank_report(self):
        clients = self._get_all_clients()
        clients_count = len(clients)
        accounts_count = len(self.bank.accounts)
        total_balance = self.bank.get_total_balance()

        processed_transactions = self.processed_transactions
        total_transactions = len(processed_transactions)

        completed_transactions = sum(
            1 for transaction in processed_transactions
            if transaction.status == TransactionStatus.COMPLETED
        )

        failed_transactions = sum(
            1 for transaction in processed_transactions
            if transaction.status == TransactionStatus.FAILED
        )

        suspicious_transactions = self.risk_analyzer.get_suspicious_operations_report()
        suspicious_count = len(suspicious_transactions)

        report = {
            "bank_name": self.bank.name,
            "clients_count": clients_count,
            "accounts_count": accounts_count,
            "total_balance": total_balance,
            "transactions": {
                "total": total_transactions,
                "completed": completed_transactions,
                "failed": failed_transactions,
            },
            "suspicious_transactions_count": suspicious_count,
        }

        return report

    def _get_all_clients(self):
        if isinstance(self.bank.clients, dict):
            return list(self.bank.clients.values())
        return list(self.bank.clients)

    def build_risk_report(self):
        suspicious_operations = self.risk_analyzer.get_suspicious_operations_report()

        risk_levels = {
            "low": 0,
            "medium": 0,
            "high": 0,
        }

        reasons_statistics = {}

        operations = []

        for item in suspicious_operations:
            transaction = item["transaction"]
            risk_level = item["risk_level"]
            reasons = item["reasons"]

            if risk_level == RiskLevel.LOW:
                risk_levels["low"] += 1
            elif risk_level == RiskLevel.MEDIUM:
                risk_levels["medium"] += 1
            elif risk_level == RiskLevel.HIGH:
                risk_levels["high"] += 1

            for reason in reasons:
                reasons_statistics[reason] = reasons_statistics.get(reason, 0) + 1

            operations.append(
                {
                    "transaction_id": transaction.transaction_id,
                    "sender_account_id": (
                        transaction.sender.account_id
                        if transaction.sender is not None
                        else None
                    ),
                    "receiver_account_id": (
                        transaction.receiver.account_id
                        if transaction.receiver is not None
                        else None
                    ),
                    "amount": transaction.amount,
                    "risk_level": risk_level.value,
                    "risk_score": item["risk_score"],
                    "reasons": reasons,
                }
            )

        report = {
            "total_suspicious": len(suspicious_operations),
            "risk_levels": risk_levels,
            "reasons_statistics": reasons_statistics,
            "operations": operations,
        }

        return report

    def _flatten_dict(self, data, parent_key="", sep="."):
        items = {}

        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key

            if isinstance(value, dict):
                items.update(self._flatten_dict(value, new_key, sep=sep))
            elif isinstance(value, list):
                items[new_key] = json.dumps(value, ensure_ascii=False)
            else:
                items[new_key] = value

        return items

    def export_to_json(self, data, filename):
        path = os.path.join(self.output_dir, filename)

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def export_to_csv(self, data, filename):
        path = os.path.join(self.output_dir, filename)

        with open(path, "w", newline="", encoding="utf-8") as file:
            if isinstance(data, dict):
                flattened_data = self._flatten_dict(data)
                writer = csv.DictWriter(file, fieldnames=flattened_data.keys())
                writer.writeheader()
                writer.writerow(flattened_data)

            elif isinstance(data, list):
                if not data:
                    return

                prepared_rows = []
                all_keys = set()

                for row in data:
                    if isinstance(row, dict):
                        flattened_row = self._flatten_dict(row)
                    else:
                        flattened_row = {"value": row}

                    prepared_rows.append(flattened_row)
                    all_keys.update(flattened_row.keys())

                fieldnames = list(all_keys)
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                for row in prepared_rows:
                    writer.writerow(row)

            else:
                writer = csv.writer(file)
                writer.writerow(["value"])
                writer.writerow([data])

    def create_transactions_pie_chart(self):
        processed_transactions = self.processed_transactions

        completed_transactions = sum(
            1 for transaction in processed_transactions
            if transaction.status == TransactionStatus.COMPLETED
        )

        failed_transactions = sum(
            1 for transaction in processed_transactions
            if transaction.status == TransactionStatus.FAILED
        )

        labels = []
        sizes = []

        if completed_transactions > 0:
            labels.append("Completed")
            sizes.append(completed_transactions)

        if failed_transactions > 0:
            labels.append("Failed")
            sizes.append(failed_transactions)

        if not sizes:
            return

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.title("Transactions Distribution")
        plt.axis("equal")

        path = os.path.join(self.charts_dir, "transactions_pie.png")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

    def create_top_clients_chart(self):
        clients_data = []

        for client in self._get_all_clients():
            accounts = self._get_client_accounts(client)
            total_balance = sum(account._balance for account in accounts)

            clients_data.append(
                {
                    "client_name": client.full_name,
                    "total_balance": total_balance,
                }
            )

        if not clients_data:
            return

        clients_data.sort(key=lambda item: item["total_balance"], reverse=True)
        top_clients = clients_data[:10]

        names = [item["client_name"] for item in top_clients]
        balances = [item["total_balance"] for item in top_clients]

        plt.figure(figsize=(10, 6))
        plt.bar(names, balances)
        plt.xticks(rotation=45, ha="right")
        plt.title("Top Clients by Balance")
        plt.xlabel("Clients")
        plt.ylabel("Balance")

        path = os.path.join(self.charts_dir, "top_clients_bar.png")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

    def create_balance_history_chart(self, client):
        accounts = self._get_client_accounts(client)
        client_account_ids = {account.account_id for account in accounts}

        if not client_account_ids:
            return

        current_total_balance = sum(account._balance for account in accounts)

        relevant_transactions = [
            transaction
            for transaction in self.processed_transactions
            if (
                    transaction.status == TransactionStatus.COMPLETED
                    and self._transaction_belongs_to_client(transaction, client_account_ids)
            )
        ]

        if not relevant_transactions:
            return

        balance_history = [current_total_balance]
        labels = ["Current balance"]

        running_balance = current_total_balance

        for index, transaction in enumerate(reversed(relevant_transactions), start=1):
            if (
                    transaction.receiver is not None
                    and transaction.receiver.account_id in client_account_ids
            ):
                running_balance -= transaction.amount

            if (
                    transaction.sender is not None
                    and transaction.sender.account_id in client_account_ids
            ):
                running_balance += transaction.amount

            balance_history.append(running_balance)
            labels.append(f"Step {index}")

        balance_history.reverse()
        labels.reverse()

        plt.figure(figsize=(10, 6))
        plt.plot(labels, balance_history, marker="o")
        plt.xticks(rotation=45, ha="right")
        plt.title(f"Balance Movement - {client.full_name}")
        plt.xlabel("Operations")
        plt.ylabel("Balance")

        path = os.path.join(self.charts_dir, f"{client.client_id}_balance_history.png")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()

    def save_charts(self, client):
        self.create_transactions_pie_chart()
        self.create_top_clients_chart()
        self.create_balance_history_chart(client)