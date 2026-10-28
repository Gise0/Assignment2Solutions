"""
问题 2: 银行账户管理系统(AI 开发)
Problem 2: Bank Account Management System (Developed by AI)
"""
from typing import List, Dict, Any, Optional


class BankAccount:
    """
    一个具有透支保护、状态转换和详细交易跟踪的银行账户模型
    A bank account model with overdraft protection, status transitions,
    and detailed transaction tracking.
    
    属性(Attributes):
        account_id (str): 账户的唯一标识符。
        owner (str):账户持有人的姓名。
        balance (float): 当前余额。
        overdraft_limit (float): 允许的最大负余额（默认：100.0）。
        status (str): 当前状态（"ACTIVE", "OVERDRAWN", "FROZEN"）。
        transaction_history (List[Dict[str, Any]]): 已交易记录的列表(list)。
    """

    def __init__(self, account_id: str, owner: str, initial_balance: float = 0.0, overdraft_limit: float = 100.0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        if overdraft_limit < 0:
            raise ValueError("Overdraft limit cannot be negative")

        self.account_id = account_id
        self.owner = owner
        self.balance = float(initial_balance)
        self.overdraft_limit = float(overdraft_limit)
        self.status = "ACTIVE"
        self.transaction_history: List[Dict[str, Any]] = []

        if initial_balance > 0:
            self.transaction_history.append({
                "type": "INITIAL_DEPOSIT",
                "amount": float(initial_balance),
                "fee": 0.0,
                "balance_after": self.balance,
                "description": "Initial account opening deposit"
            })

    def deposit(self, amount: float) -> bool:
        """
        向账户存钱
        
        参数(Args):
            amount (float): 要存入的金额（必须大于 0）。
            
        返回(Returns):
            bool: 若存款成功则为 True。
            
        引发(Raises):
            ValueError: 如果 amount <= 0。
            RuntimeError: 如果账户处于 FROZEN 状态。
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        if self.status == "FROZEN":
            raise RuntimeError("Cannot deposit into a frozen account")

        self.balance += float(amount)
        if self.balance >= 0 and self.status == "OVERDRAWN":
            self.status = "ACTIVE"

        self.transaction_history.append({
            "type": "DEPOSIT",
            "amount": float(amount),
            "fee": 0.0,
            "balance_after": self.balance,
            "description": f"Deposit of ${amount:.2f}"
        })
        return True

    def withdraw(self, amount: float, fee: float = 0.0) -> bool:
        """
        从账户取款（可附带交易手续费）
        
        参数(Args):
            amount (float): 要提取的金额(必须大于 0)
            fee (float): 额外提款手续费(默认: 0.0, 必须 >= 0)
            
        返回(Returns):
            bool: 若提款成功则为 True。
            
        引发(Raises):
            ValueError: 如果 amount <= 0、fee < 0, 或总额超过 balance + overdraft_limit。
            RuntimeError: 如果账户处于 FROZEN 状态。
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if fee < 0:
            raise ValueError("Fee cannot be negative")
        if self.status == "FROZEN":
            raise RuntimeError("Cannot withdraw from a frozen account")

        total_deduction = float(amount + fee)
        if self.balance - total_deduction < -self.overdraft_limit:
            raise ValueError(f"Insufficient funds: withdrawal would exceed overdraft limit of ${self.overdraft_limit:.2f}")

        self.balance -= total_deduction
        if self.balance < 0:
            self.status = "OVERDRAWN"

        self.transaction_history.append({
            "type": "WITHDRAWAL",
            "amount": float(amount),
            "fee": float(fee),
            "balance_after": self.balance,
            "description": f"Withdrawal of ${amount:.2f} (Fee: ${fee:.2f})"
        })
        return True

    def transfer_to(self, target_account: "BankAccount", amount: float, transfer_fee: float = 0.0) -> bool:
        """
        将资金转账到另一个 BankAccount
        
        参数(Args):
            target_account (BankAccount): 收款账户
            amount (float): 要转账的金额(必须大于 0)
            transfer_fee (float): 收取发款方的手续费(默认: 0.0)
            
        返回(Returns):
            bool: 若转账成功则为 True。
            
        引发(Raises):
            TypeError: 如果 target_account 不是 BankAccount。
            RuntimeError: 如果任一账户处于 FROZEN 状态。
            ValueError: 如果 amount <= 0 或发送方资金不足。
        """
        if not isinstance(target_account, BankAccount):
            raise TypeError("Target account must be an instance of BankAccount")
        if self.status == "FROZEN":
            raise RuntimeError("Cannot transfer from a frozen account")
        if target_account.status == "FROZEN":
            raise RuntimeError("Cannot transfer to a frozen account")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        # 从发送方扣款Deduct from sender 
        self.withdraw(amount, fee=transfer_fee)

        # 向收款方存款 Deposit to recipient
        target_account.deposit(amount)
        return True

    def freeze(self) -> None:
        """
        冻结账户(阻止存款和取款)
        """
        self.status = "FROZEN"

    def unfreeze(self) -> None:
        """
        解冻账户(恢复为合适的 ACTIVE 或 OVERDRAWN 状态)
        """
        self.status = "OVERDRAWN" if self.balance < 0 else "ACTIVE"

    def get_summary(self) -> Dict[str, Any]:
        """
        返回当前账户状态的摘要字典
        """
        return {
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": round(self.balance, 2),
            "status": self.status,
            "overdraft_limit": self.overdraft_limit,
            "transaction_count": len(self.transaction_history)
        }
