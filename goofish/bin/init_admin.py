import argparse
from db_manager import db_manager


def main(admin_email="admin@noreply.org"):
    parser = argparse.ArgumentParser(description="初始化或重置管理员账号")
    parser.add_argument("--pass", dest="password", required=True, help="管理员密码")
    args = parser.parse_args()
    password = args.password.strip()
    if not password:
        raise SystemExit("密码不能为空")

    existing = db_manager.get_user_by_username("admin")
    if existing:
        print("admin 用户已存在，将重置密码")
        ok = db_manager.update_user_password("admin", password)
        if not ok:
            raise SystemExit("重置 admin 密码失败")
        # 确保仍为管理员
        with db_manager.lock:
            cursor = db_manager.conn.cursor()
            cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'admin'")
            db_manager.conn.commit()

        print("重置完成：已更新 admin 密码")
        return

    print("=== 初始化管理员账号 (CLI) ===")
    ok = db_manager.create_user("admin", admin_email, password)
    if not ok:
        raise SystemExit("创建 admin 用户失败：用户名或邮箱可能已存在")
    # 设为管理员
    with db_manager.lock:
        cursor = db_manager.conn.cursor()
        cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'admin'")
        db_manager.conn.commit()

    print("初始化完成：已创建 admin 用户")


if __name__ == "__main__":
    main()
