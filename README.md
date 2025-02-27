# 國立高雄科技大學 智慧商務系友會 後端伺服器

## 專案簡介
本專案為智慧商務系友會的後端伺服器，旨在提供可靠、高效且易於擴展的後端支援系統。專案採用 Django 框架，並整合多項現代化技術來處理 RESTful API、任務佇列、資料庫操作及資料分析。

## 技術棧與套件
以下是本專案使用到的主要技術與套件：

- **Django (5.0.2):** 後端框架，用於構建高效的 Web 應用程式。
- **Django REST Framework (3.14.0):** RESTful API 的核心。
- **SimpleJWT (5.3.1):** 用於 JWT 驗證的輕量化工具。
- **Celery (5.4.0):** 任務佇列，用於非同步任務處理。
- **Redis (5.2.1):** 作為 Celery 的訊息代理。
- **MySQL:** 資料庫，透過 `mysqlclient` 及 `PyMySQL` 進行連接。
- **Drf-yasg (1.21.7):** 提供 API 文件自動生成功能。
- **Python-crontab (3.2.0):** 排程任務管理。
- **Numpy, Pandas, Scipy:** 提供數據處理與科學計算功能。
- **Matplotlib, Seaborn:** 資料視覺化工具。
- **Mlxtend:** 提供擴展的機器學習功能。

## 專案結構
```
project_root/
├── config/                # 專案設定檔案
├── apps/                  # 應用模組目錄
├── tasks/                 # Celery 任務相關模組
├── static/                # 靜態資源
├── templates/             # HTML 模板
├── requirements.txt       # 套件需求清單
├── .env                   # 環境變數設定檔案
└── README.md               # 專案說明文件
```

## 安裝與執行

### 1. 安裝環境需求
確保您已安裝以下工具：
- Python 3.10 或更新版本
- MySQL 資料庫
- Redis 伺服器

### 2. 克隆專案
```bash
git clone https://github.com/NameCallBob/nkust_icalumni_backend.git
cd project_root
```

### 3. 安裝依賴套件
建議使用虛擬環境來隔離專案依賴：
```bash
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 配置環境變數
建立 `.env` 文件並填入必要的設定：

### 5. 初始化資料庫
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 啟動伺服器
啟動開發伺服器：
```bash
python manage.py runserver ?
```

啟動 Celery：
```bash
celery -A IC_alumni worker --loglevel=info
```

啟動 Celery Beat（如有需要）：
```bash
celery -A IC_alumni beat --loglevel=info
```

## API 文件
使用 `drf-yasg` 提供的 Swagger 文件：
訪問 [http://127.0.0.1:8000/server/api/swagger/](http://127.0.0.1:8000/server/api/swagger/) 以查看 API 文件。


## 貢獻方式
歡迎任何形式的貢獻，請遵循以下步驟：
1. Fork 本專案。
2. 建立分支並提交您的更改。
3. 發送 Pull Request，描述您的更改內容。

## 授權
本專案採用 MIT License 授權。

---

如有任何問題或建議，請聯絡我們的開發團隊！

