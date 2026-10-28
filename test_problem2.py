"""
问题 2单元测试: BankAccount

说明：
使用 Python 的 unittest 框架补全下面的测试方法。
你的测试方法必须断言 BankAccount 对象上的多个属性
（例如 balance、status、transaction_history、summary）以验证状态一致性。

运行测试：
    python -m unittest test_problem2.py -v
"""
import unittest
from problem2 import BankAccount


class TestBankAccount(unittest.TestCase):

    def setUp(self):
        """
        Set up test fixtures before each test method.
        在每个测试方法执行前设置测试夹具（test fixtures）。
        """
        self.account_empty = BankAccount("ACC001", "Alice", initial_balance=0.0, overdraft_limit=100.0)
        self.account_funded = BankAccount("ACC002", "Bob", initial_balance=200.0, overdraft_limit=50.0)

    def test_initial_state_multi_attributes(self):
        """
        验证新创建的账户是否正确初始化所有属性。
        检查 balance、owner、status、overdraft_limit、transaction_history 和 summary。
        """
        # 测试空账户
        self.assertEqual(self.account_empty.balance, 0.0)
        self.assertEqual(self.account_empty.owner, "Alice")
        self.assertEqual(self.account_empty.account_id, "ACC001")
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.assertEqual(self.account_empty.overdraft_limit, 100.0)
        self.assertEqual(len(self.account_empty.transaction_history), 0)

        # 测试存款账户
        self.assertEqual(self.account_funded.balance, 200.0)
        self.assertEqual(self.account_funded.owner, "Bob")
        self.assertEqual(self.account_funded.account_id, "ACC002")
        self.assertEqual(self.account_funded.status, "ACTIVE")
        self.assertEqual(self.account_funded.overdraft_limit, 50.0)
        self.assertEqual(len(self.account_funded.transaction_history), 1)
        self.assertEqual(self.account_funded.transaction_history[0]["type"], "INITIAL_DEPOSIT")
        self.assertEqual(self.account_funded.transaction_history[0]["amount"], 200.0)

        # 测试 get_summary
        summary = self.account_empty.get_summary()
        self.assertEqual(summary["account_id"], "ACC001")
        self.assertEqual(summary["owner"], "Alice")
        self.assertEqual(summary["balance"], 0.0)
        self.assertEqual(summary["status"], "ACTIVE")
        self.assertEqual(summary["overdraft_limit"], 100.0)
        self.assertEqual(summary["transaction_count"], 0)

    def test_deposit_updates_multiple_attributes(self):
        """
        测试存款是否正确更新 balance、transaction_history 和 summary
        """
        # 向空账户存入 $150
        result = self.account_empty.deposit(150.0)
        self.assertTrue(result)
        self.assertEqual(self.account_empty.balance, 150.0)
        self.assertEqual(len(self.account_empty.transaction_history), 1)
        self.assertEqual(self.account_empty.transaction_history[0]["type"], "DEPOSIT")
        self.assertEqual(self.account_empty.transaction_history[0]["amount"], 150.0)
        self.assertEqual(self.account_empty.transaction_history[0]["balance_after"], 150.0)

        # 验证 summary 更新
        summary = self.account_empty.get_summary()
        self.assertEqual(summary["balance"], 150.0)
        self.assertEqual(summary["transaction_count"], 1)

        # 多次存款
        self.account_empty.deposit(50.0)
        self.assertEqual(self.account_empty.balance, 200.0)
        self.assertEqual(len(self.account_empty.transaction_history), 2)

    def test_withdrawal_within_balance_multi_attributes(self):
        """
        测试当余额充足时提款是否正确
        """
        # 从 funded 账户提取 $50，附带 $2.50 手续费
        result = self.account_funded.withdraw(50.0, fee=2.50)
        self.assertTrue(result)
        self.assertEqual(self.account_funded.balance, 147.50)  # 200 - 50 - 2.50
        self.assertEqual(len(self.account_funded.transaction_history), 2)  # INITIAL_DEPOSIT + WITHDRAWAL
        self.assertEqual(self.account_funded.transaction_history[1]["type"], "WITHDRAWAL")
        self.assertEqual(self.account_funded.transaction_history[1]["amount"], 50.0)
        self.assertEqual(self.account_funded.transaction_history[1]["fee"], 2.50)
        self.assertEqual(self.account_funded.transaction_history[1]["balance_after"], 147.50)
        self.assertEqual(self.account_funded.status, "ACTIVE")

        # 验证 summary
        summary = self.account_funded.get_summary()
        self.assertEqual(summary["balance"], 147.50)
        self.assertEqual(summary["transaction_count"], 2)

    def test_overdraft_withdrawal_and_status_transition(self):
        """
        测试使用透支保护的提款 (余额变为负数，但仍 >= -overdraft_limit)
        """
        # 从空账户提取 $50（余额 0，透支上限 100）
        result = self.account_empty.withdraw(50.0)
        self.assertTrue(result)
        self.assertEqual(self.account_empty.balance, -50.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")
        self.assertEqual(len(self.account_empty.transaction_history), 1)

        # 测试透支边界：提取刚好等于透支上限的金额
        account2 = BankAccount("ACC003", "Carol", initial_balance=0.0, overdraft_limit=100.0)
        result = account2.withdraw(100.0)  # 余额变为 -100，刚好等于 overdraft_limit
        self.assertTrue(result)
        self.assertEqual(account2.balance, -100.0)
        self.assertEqual(account2.status, "OVERDRAWN")

        # 测试超出透支上限应抛出异常
        with self.assertRaises(ValueError):
            account2.withdraw(1.0)  # -100 - 1 = -101 < -100

    def test_deposit_recovering_from_overdrawn_status(self):
        """
        测试当存款足以使余额 >= 0 时，状态从 OVERDRAWN 转回 ACTIVE。
        """
        # 先从空账户透支
        self.account_empty.withdraw(50.0)
        self.assertEqual(self.account_empty.status, "OVERDRAWN")
        self.assertEqual(self.account_empty.balance, -50.0)

        # 存款使余额回到正数
        self.account_empty.deposit(100.0)
        self.assertEqual(self.account_empty.balance, 50.0)
        self.assertEqual(self.account_empty.status, "ACTIVE")

        # 存款刚好使余额为 0
        account2 = BankAccount("ACC004", "Dave", initial_balance=0.0, overdraft_limit=100.0)
        account2.withdraw(30.0)
        self.assertEqual(account2.status, "OVERDRAWN")
        account2.deposit(30.0)
        self.assertEqual(account2.balance, 0.0)
        self.assertEqual(account2.status, "ACTIVE")

    def test_transfer_between_accounts_multi_attributes(self):
        """
        测试两个账户之间的资金转账。
        """
        # 记录转账前状态
        sender_balance_before = self.account_funded.balance
        receiver_balance_before = self.account_empty.balance

        # 从 account_funded 转账 $50 到 account_empty，收取 $5 手续费
        result = self.account_funded.transfer_to(self.account_empty, 50.0, transfer_fee=5.0)
        self.assertTrue(result)

        # 验证发送方余额：200 - 50 - 5 = 145
        self.assertEqual(self.account_funded.balance, 145.0)
        # 验证收款方余额：0 + 50 = 50
        self.assertEqual(self.account_empty.balance, 50.0)

        # 验证交易记录
        self.assertEqual(len(self.account_funded.transaction_history), 2)  # INITIAL_DEPOSIT + WITHDRAWAL
        self.assertEqual(len(self.account_empty.transaction_history), 1)  # DEPOSIT

        # 验证转账后状态
        self.assertEqual(self.account_funded.get_summary()["balance"], 145.0)
        self.assertEqual(self.account_empty.get_summary()["balance"], 50.0)

    def test_frozen_account_restrictions(self):
        """
        测试 FROZEN 账户在存款、取款和转账时会抛出 RuntimeError。
        """
        # 冻结账户
        self.account_empty.freeze()
        self.assertEqual(self.account_empty.status, "FROZEN")

        # 测试冻结账户存款抛出 RuntimeError
        with self.assertRaises(RuntimeError):
            self.account_empty.deposit(100.0)

        # 测试冻结账户取款抛出 RuntimeError
        with self.assertRaises(RuntimeError):
            self.account_empty.withdraw(50.0)

        # 测试冻结账户转账抛出 RuntimeError
        with self.assertRaises(RuntimeError):
            self.account_empty.transfer_to(self.account_funded, 50.0)

        # 测试向冻结账户转账抛出 RuntimeError
        account_frozen = BankAccount("ACC005", "Eve", initial_balance=0.0)
        account_frozen.freeze()
        with self.assertRaises(RuntimeError):
            self.account_funded.transfer_to(account_frozen, 50.0)

        # 测试解冻后恢复正常
        self.account_empty.unfreeze()
        self.assertEqual(self.account_empty.status, "ACTIVE")
        self.account_empty.deposit(100.0)  # 应该成功
        self.assertEqual(self.account_empty.balance, 100.0)

    def test_invalid_operations_raise_exceptions(self):
        """
        测试异常处理。
        """
        # 测试负数余额初始化
        with self.assertRaises(ValueError):
            BankAccount("ACC006", "Frank", initial_balance=-10.0)

        # 测试负数透支上限
        with self.assertRaises(ValueError):
            BankAccount("ACC007", "Grace", initial_balance=0.0, overdraft_limit=-50.0)

        # 测试存款负数金额
        with self.assertRaises(ValueError):
            self.account_empty.deposit(-10.0)

        # 测试存款零金额
        with self.assertRaises(ValueError):
            self.account_empty.deposit(0.0)

        # 测试取款负数金额
        with self.assertRaises(ValueError):
            self.account_empty.withdraw(-50.0)

        # 测试取款负数手续费
        with self.assertRaises(ValueError):
            self.account_funded.withdraw(50.0, fee=-5.0)

        # 测试取款超额（超过透支上限）
        with self.assertRaises(ValueError):
            self.account_empty.withdraw(101.0)  # 余额0 + 透支100 = 最多取100

        # 测试转账给非BankAccount对象
        with self.assertRaises(TypeError):
            self.account_funded.transfer_to("not_an_account", 50.0)

        # 测试转账负数金额
        with self.assertRaises(ValueError):
            self.account_funded.transfer_to(self.account_empty, -50.0)


if __name__ == "__main__":
    unittest.main()
