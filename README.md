# 高雄科技大學 智慧商務系友會 — 後端 API 伺服器

國立高雄科技大學智慧商務系系友會官方網站的後端服務，以 Django REST Framework 提供 JWT 驗證的 RESTful API，支撐系友資料管理、企業/徵才媒合、活動與文章發布、系所簡介內容管理等功能。

- 正式環境 API：`https://nkust-alumni-api.binbinbob.work`
- 對應前端：[nkust_icalumni_frontend](https://github.com/NameCallBob/nkust_icalumni_frontend)（`https://aaic.nkust.edu.tw`）

## 目錄

- [功能模組](#功能模組)
- [技術棧](#技術棧)
- [專案結構](#專案結構)
- [本機開發環境設置](#本機開發環境設置)
- [環境變數](#環境變數)
- [測試](#測試)
- [API 文件](#api-文件)
- [資安設計](#資安設計)
- [CI](#ci)

## 功能模組

| App | 說明 |
|---|---|
| `apps/private` | 帳號認證核心（Email + JWT），密碼重設、忘記密碼流程 |
| `apps/member` | 系友會員資料、職位、學籍、傑出系友、會員自助中心 |
| `apps/company` | 系友創業/任職企業資訊、企業搜尋 |
| `apps/product` | 企業產品/服務展示 |
| `apps/recruit` | 徵才資訊發布與查詢 |
| `apps/picture` | 首頁輪播圖、彈跳廣告、圖片素材管理 |
| `apps/article` | 電子報／文章發布（CKEditor 富文本） |
| `apps/Info` | 系友會簡介、加入辦法、章程、幹部等靜態內容管理 |
| `apps/notice` | 系統通知信（帳號建立、忘記密碼、登入通知），透過 Resend API 寄送，SMTP 為備援 |
| `apps/record` | 請求監控/存取記錄、聯絡表單 |
| `apps/seo` | SEO 相關輔助端點 |

## 技術棧

- **Django 5.0** + **Django REST Framework** — API 框架
- **djangorestframework-simplejwt** — JWT 驗證與黑名單
- **MySQL**（`mysqlclient`）— 主資料庫
- **Redis**（`django-redis`）— 快取
- **drf-yasg** — Swagger / Redoc API 文件（僅在 `DEBUG` 或 `EXPOSE_API_DOCS=1` 時對外開放）
- **django-ckeditor** — 文章/簡介富文本編輯
- **Resend**（`resend`）— 交易型郵件主要通道，SMTP 為備援
- **GeoIP2**（MaxMind GeoLite2）— 依 IP 取得國別，用於監控/風控
- **gunicorn** + **whitenoise** — 正式環境伺服應用與靜態檔

> 舊版 `requirements.txt` 混雜大量與本專案無關的機器學習套件（TensorFlow/PyTorch/YOLO 等），已於 2026-07 清理，改以實際 venv 匯出的套件清單為準。

## 專案結構

```
IC_alumni/
├── IC_alumni/              # 專案設定（settings.py, urls.py, middlewares/, permission/, log/）
├── apps/                   # 各業務模組（見上表）
├── geoip/                  # GeoLite2 資料庫
├── static/                 # 靜態資源（ckeditor、drf-yasg 等第三方套件靜態檔）
├── requirements.txt        # 套件需求清單
├── run_gunicorn.sh         # 正式環境啟動腳本
├── .github/workflows/ci.yml# CI：語法檢查、Django check、migration 檢查、測試
└── manage.py
```

## 本機開發環境設置

### 需求

- Python 3.12+
- MySQL（本機可用 Docker 起一個容器）
- （選用）Redis

### 步驟

```bash
git clone https://github.com/NameCallBob/nkust_icalumni_backend.git
cd IC_alumni

python -m venv venv-alumni
source venv-alumni/bin/activate      # Windows: venv-alumni\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                 # 依下方「環境變數」章節填入實際值
python manage.py migrate
python manage.py seed_demo           # 建立可重複執行的 demo 種子資料（不寄信）

python manage.py runserver 127.0.0.1:8001 --noreload
```

> macOS 上 `mysqlclient` 編譯需要 `brew install mysql-client`，並將其 `bin` 目錄加入 `PATH`。

Demo 帳號（`seed_demo` 建立）：`admin@demo.local` / `alice@demo.local`，密碼 `Demo#1234`（可用 `SEED_DEMO_PASSWORD` 覆寫）。`seed_demo` 預設拒絕在非 `DEBUG` 環境執行，避免正式環境誤建立已知密碼的帳號。

## 環境變數

| 變數 | 說明 | 預設 |
|---|---|---|
| `SECRET_KEY` | Django 密鑰，同時作為 JWT 簽章金鑰預設值 | 必填 |
| `JWT_SIGNING_KEY` | JWT 簽章金鑰，未設定則沿用 `SECRET_KEY` | 選填 |
| `SERVER_IP` / `SERVER_DATABASE` / `SERVER_USER` / `SERVER_PWD` | MySQL 連線設定（`SERVER_IP` 本機請用 `127.0.0.1`，`localhost` 會走不存在的 socket） | 必填 |
| `RESEND_API_KEY` / `RESEND_FROM_EMAIL` | 交易型郵件（Resend API） | 選填 |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | SMTP 備援寄信 | 選填 |
| `EXPOSE_API_DOCS` | 是否對外開放 Swagger/Redoc（正式環境預設關閉） | `0` |
| `ENABLE_DEV_ORIGINS` | 是否允許任意 port 的 `localhost`/`127.0.0.1` CORS 來源（僅供本機開發） | `0` |
| `ENABLE_HTTPS_SECURITY` | 是否啟用 HSTS / Secure Cookie 等正式環境安全標頭（已有 HTTPS 的正式部署請設為 `1`） | `0` |
| `TRUSTED_PROXY_COUNT` | 反向代理層數，用於正確解析 `X-Forwarded-For` | `0` |
| `SEED_DEMO_PASSWORD` / `ALLOW_SEED_DEMO` | 覆寫 demo 種子密碼／允許在非 DEBUG 環境執行 seed | — |

## 測試

```bash
python manage.py test
```

`apps/member/test_security_fixes.py` 為資安修補的回歸測試（自助提權、IDOR、欄位擁有者過濾等）。

## API 文件

正式環境預設關閉 API 文件（避免完整曝露 API 結構）。本機開發（`DEBUG=True`）或設定 `EXPOSE_API_DOCS=1` 後：

- Swagger: `/server/api/swagger/`
- Redoc: `/server/api/redoc/`

## 資安設計

- **預設拒絕**：DRF `DEFAULT_PERMISSION_CLASSES` 為 `IsAuthenticated`，公開端點須於各 view/action 明確標註 `AllowAny`。
- 會員自助更新（`private_input`）僅白名單允許 `email`，`is_staff`/`is_superuser`/`is_active`/密碼一律由伺服端專用流程處理，無法透過一般序列化欄位覆寫。
- 忘記密碼、帳號查詢等端點皆已處理「帳號列舉」風險（不因回應差異洩漏帳號是否存在）。
- 圖片/檔案上傳採內容嗅探（非僅信任副檔名）與大小限制。
- `X-Forwarded-For` 僅信任 `TRUSTED_PROXY_COUNT` 指定層數之後的 hop，避免用戶端偽造來源 IP。

完整歷史稽核紀錄與修補明細見 `SECURITY_PERFORMANCE_REPORT.md`。已知待辦（非阻斷）：CKEditor 4 已無官方安全更新、需評估升級至 CKEditor 5；金鑰輪換排程。

## CI

`.github/workflows/ci.yml` 於每次 push/PR 執行語法檢查（flake8 blocking rules）、`manage.py check`、migration 一致性檢查、與完整測試套件，不含自動部署，部署仍由人工執行。
