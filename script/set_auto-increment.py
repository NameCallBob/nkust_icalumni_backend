import pymysql
from dotenv import load_dotenv
import os 

load_dotenv()

# 資料庫連線配置
DB_CONFIG = {
    "host": os.getenv("SERVER_IP"),        # 資料庫主機
    "user": os.getenv("SERVER_USER"),        # 資料庫使用者
    "password": os.getenv("SERVER_PWD"),    # 資料庫密碼
    "database": os.getenv("SERVER_DATABASE"),    # 資料庫名稱
    "charset": "utf8mb4",         # 字元編碼
    "port": os.getenv("SERVER_PORT")         # 資料庫連接埠
}

def get_primary_keys_without_auto_increment(connection):
    """
    查詢所有主鍵欄位中尚未設置 AUTO_INCREMENT 的表與欄位資訊。
    """
    query = """
    SELECT TABLE_NAME, COLUMN_NAME
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = %s
      AND COLUMN_KEY = 'PRI'
      AND EXTRA NOT LIKE '%%auto_increment%%';
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (DB_CONFIG["database"],))
        results = cursor.fetchall()
    return results

def set_auto_increment(connection, table_name, column_name):
    """
    將指定表的主鍵欄位設定為 AUTO_INCREMENT。
    """
    query = f"ALTER TABLE `{table_name}` MODIFY `{column_name}` INT NOT NULL AUTO_INCREMENT;"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
        connection.commit()
        print(f"成功為表 `{table_name}` 的欄位 `{column_name}` 設定 AUTO_INCREMENT")
    except pymysql.MySQLError as e:
        print(f"設定失敗：表 `{table_name}` 的欄位 `{column_name}` -> {e}")

def main():
    """
    主程式：檢測並批量設定 AUTO_INCREMENT。
    """
    try:
        # 建立資料庫連線
        connection = pymysql.connect(**DB_CONFIG)

        # 查詢主鍵欄位中尚未設置 AUTO_INCREMENT 的欄位
        results = get_primary_keys_without_auto_increment(connection)
        if not results:
            print("所有主鍵欄位均已設置 AUTO_INCREMENT，無需修改。")
            return

        # 對每個需要修改的表進行操作
        for table_name, column_name in results:
            set_auto_increment(connection, table_name, column_name)

    except pymysql.MySQLError as e:
        print(f"資料庫連接或操作錯誤：{e}")

    finally:
        # 關閉資料庫連線
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    main()
