"""
纯框架：个人财务管理系统骨架。

包含模块：
- 数据库存取层：用户表、账单表接口。
- 远程网络层：客户端 / 服务端通信及登录验证。
- 用户界面层：区分普通用户与管理员操作。

建议拆分到多个 Python 文件（自行新建）：
- `storage_backend.py`：实现 `StorageBackend` 接口（例如 SQLite 逻辑）。
- `server.py`：实现 `FinanceServer` 与 `FinanceRequestHandler` 的细节。
- `client.py`：实现 `FinanceClient` 与业务协议。
- `ui.py`：实现 `ClientUI` 或替换为 GUI/Web。

实际业务逻辑、SQL 与网络协议需自行填充。
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Protocol


DB_PATH = Path(__file__).with_name("finance.db")


class StorageBackend(Protocol):
    """存储层接口，定义用户和账单的 CRUD 操作。"""

    def initialize(self) -> None: ...

    def authenticate(self, username: str, password: str) -> Optional["User"]:
        ...

    def fetch_user_records(self, user_id: int) -> List["Bill"]:
        ...

    def fetch_all_records(self) -> List["Bill"]:
        ...

    def upsert_record(self, bill: "Bill") -> None:
        ...

    def list_users(self) -> List["User"]:
        ...

    def create_user(self, user: "User") -> None:
        ...


@dataclass
class User:
    username: str
    password: str
    role: str  # "admin" 或 "user"
    id: Optional[int] = None


@dataclass
class Bill:
    user_id: int
    kind: str  # "income" or "expense"
    amount: float
    category: str
    notes: str = ""
    id: Optional[int] = None


class SQLiteDatabase(StorageBackend):
    """
    SQLite 实现骨架，仅定义方法结构。

    建议把真实实现放到 `storage/sqlite_impl.py`（需新建），
    然后在此文件中按需导入，保持 main 只作为入口。
    """

    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path

    def initialize(self) -> None:
        # 初始化数据库结构，例如创建 users / transactions 表。
        raise NotImplementedError("创建 users 与 transactions 两张表")

    def authenticate(self, username: str, password: str) -> Optional[User]:
        # 根据用户名密码查询用户并返回 User 实例。
        raise NotImplementedError

    def fetch_user_records(self, user_id: int) -> List[Bill]:
        # 返回指定用户的全部账单记录。
        raise NotImplementedError

    def fetch_all_records(self) -> List[Bill]:
        # 管理员使用：一次性返回所有用户的账单记录。
        raise NotImplementedError

    def upsert_record(self, bill: Bill) -> None:
        # 新增或更新一条账单记录。
        raise NotImplementedError

    def list_users(self) -> List[User]:
        # 管理员使用：列出所有用户及其角色。
        raise NotImplementedError

    def create_user(self, user: User) -> None:
        # 管理员使用：创建新账号并写入数据库。
        raise NotImplementedError


@dataclass
class Session:
    """保存当前登录会话."""

    user: User
    token: str  # 可以换成实际的 session id


class FinanceServer:
    """
    服务端框架：负责网络监听、登录验证、记录同步。

    推荐在 `server/server_core.py`（需新建）里实现 socket/HTTP 细节，
    这里仅声明接口，方便在不同协议间切换。
    """

    def __init__(self, host: str, port: int, storage: StorageBackend) -> None:
        self.host = host
        self.port = port
        self.storage = storage

    def start(self) -> None:
        # 启动监听循环，接受客户端连接。
        raise NotImplementedError("初始化 socket/HTTP 服务，接受客户端连接")

    def stop(self) -> None:
        # 优雅关闭服务端资源。
        raise NotImplementedError


class FinanceRequestHandler:
    """
    单个客户端连接的处理器骨架。

    具体解析协议、业务分发等逻辑建议单独放到
    `server/handlers.py`（需新建）中，以便维护。
    """

    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.session: Optional[Session] = None

    def dispatch(self, payload: Dict[str, str]) -> Dict[str, str]:
        """
        payload 示例：
        {
            "action": "login|logout|fetch|update|list_users|create_user",
            "data": {...}
        }
        """
        raise NotImplementedError("根据 action 分发到不同处理函数")

    def _handle_login(self, username: str, password: str) -> Dict[str, str]:
        # 处理 login 请求，成功后建立 Session。
        raise NotImplementedError

    def _handle_logout(self) -> Dict[str, str]:
        # 清除 Session，让客户端重新登录。
        raise NotImplementedError

    def _handle_fetch(self, scope: str) -> Dict[str, str]:
        # 根据 scope=own/all 返回不同范围的账单数据。
        raise NotImplementedError

    def _handle_update(self, bill_data: Dict[str, str]) -> Dict[str, str]:
        # 普通用户更新自己的记录，管理员可指定 user_id。
        raise NotImplementedError

    def _handle_admin_actions(self, payload: Dict[str, str]) -> Dict[str, str]:
        raise NotImplementedError("管理员可查看所有用户记录、统计图表等")

    def _require_login(self) -> Session:
        # 没有 Session 时返回错误或抛异常，保证后续操作安全。
        raise NotImplementedError("若未登录则抛出异常/返回错误信息")


class FinanceClient:
    """
    客户端通信骨架，负责连接远程服务端。

    建议在 `client/transport.py`（需新建）里完成协议细节，实现连接、
    请求封装等，这里只定义接口，方便替换实现。
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def connect(self) -> None:
        # 建立网络连接，失败时抛出异常供 UI 捕获。
        raise NotImplementedError("建立 TCP/HTTP 连接")

    def login(self, username: str, password: str) -> Dict[str, str]:
        # 发送 login 请求并返回服务端响应。
        raise NotImplementedError

    def logout(self) -> None:
        # 发送 logout 请求，释放会话。
        raise NotImplementedError

    def fetch_records(self, scope: str = "own") -> List[Bill]:
        # scope="own" 获取自身记录，scope="all" 供管理员使用。
        raise NotImplementedError

    def update_record(self, bill: Bill) -> None:
        # 提交新增/修改账单的请求。
        raise NotImplementedError

    def list_users(self) -> List[User]:
        # 管理员功能：获取所有用户信息。
        raise NotImplementedError

    def create_user(self, user: User) -> None:
        # 管理员功能：创建用户并设置角色。
        raise NotImplementedError


class ClientUI:
    """
    用户界面骨架：可替换为 CLI、GUI 或 Web 前端。

    可以在 `ui/cli.py` 或 GUI 对应文件（需新建）中完善交互逻辑。
    """

    def __init__(self, client: FinanceClient) -> None:
        self.client = client
        self.session: Optional[Session] = None

    def run(self) -> None:
        self._login_flow()
        self._main_menu()

    def _login_flow(self) -> None:
        # 负责收集用户输入并调用 client.login。
        raise NotImplementedError("输入账号密码，调用 client.login")

    def _main_menu(self) -> None:
        """
        伪代码：
            if session.user.role == 'admin':
                展示管理员菜单（拉取所有记录、统计、创建用户等）
            else:
                展示普通用户菜单（查看/更新自己的记录）
        """
        raise NotImplementedError


def run_server(host: str, port: int) -> None:
    # 框架入口：初始化存储与服务端，供 main 调用。
    storage = SQLiteDatabase()
    storage.initialize()
    server = FinanceServer(host, port, storage)
    server.start()


def run_client(host: str, port: int) -> None:
    # 框架入口：初始化客户端与 UI，建立远程连接。
    client = FinanceClient(host, port)
    client.connect()
    ui = ClientUI(client)
    ui.run()


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    # 解析命令行参数，区分 server/client 模式。
    parser = argparse.ArgumentParser(description="Finance framework skeleton")
    sub = parser.add_subparsers(dest="mode", required=True)

    srv = sub.add_parser("server", help="启动远程服务端")
    srv.add_argument("--host", default="0.0.0.0")
    srv.add_argument("--port", type=int, default=9000)

    cli = sub.add_parser("client", help="启动远程客户端")
    cli.add_argument("--host", default="127.0.0.1")
    cli.add_argument("--port", type=int, default=9000)

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    if args.mode == "server":
        run_server(args.host, args.port)
    else:
        run_client(args.host, args.port)


if __name__ == "__main__":
    main(sys.argv[1:])

