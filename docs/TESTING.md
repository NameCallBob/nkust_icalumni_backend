# 測試指南（後端 IC_alumni）

本專案是公開 repo，測試體系的目標不只是「有測試」，而是讓**任何人送 PR 之後，
CI 能清楚指出這次改動可能造成什麼問題**。

---

## 快速開始

```bash
# 1. 安裝（正式 + 開發相依）
make install

# 2. 跑全部測試
make test

# 3. 看覆蓋率
make cov-html   # 產生 reports/coverage-html/index.html
```

不需要 MySQL、不需要 Redis、不需要 `.env`。全部測試在 SQLite in-memory 上執行，
郵件走 locmem，對外網路連線被封鎖。整套跑完約 3 秒。

---

## 這套測試會抓到什麼

| 你做的改動 | 會失敗的測試 | 為什麼重要 |
|---|---|---|
| 新增一支 API 端點 | `contracts/test_route_inventory.py` | 強迫介面變動被 review 看到 |
| 把某支端點改成 `AllowAny` | `test_public_surface_did_not_grow` | 攻擊面擴大必須是明確決定 |
| 忘記在新 view 上加權限 | `contracts/test_permission_matrix.py` | 實際發匿名請求驗證，不是只看宣告 |
| 在公開序列化器多加一個欄位 | `security/test_pii_leakage.py` | 電話／地址／生日一旦外洩無法回收 |
| 移除 queryset 的 `select_related` | `test_performance_budget.py` | N+1 在小資料量下完全看不出來 |
| 放寬某項安全設定 | `security/test_settings_hardening.py` | 讀的是正式設定模組，改測試設定沒用 |
| 改了模型忘了產生 migration | `test_migrations.py` | 部署當下才爆的典型失誤 |
| 不小心 `git add` 了 `.env` | `security/test_repo_hygiene.py` | 公開 repo 的密鑰外洩無法補救 |

---

## 目錄結構

```
tests/
├── settings_test.py        # 離線測試設定（SQLite / locmem / 無節流 / 無監控中介層）
├── conftest.py             # 全域夾具 + autouse 防護（封網路、攔寄信、清快取）
├── factories.py            # 模型工廠——建測試資料的唯一管道
├── route_map.py            # URLconf 自省：把 220 條路由變成可斷言的資料
├── helpers.py              # 共用小工具
│
├── contracts/              # API 介面契約
│   ├── routes_baseline.json      # 路由清單基準檔（自動產生，勿手改）
│   ├── update_baseline.py        # 重新產生基準檔的腳本
│   ├── test_route_inventory.py   # 介面／權限變動偵測
│   └── test_permission_matrix.py # 逐路由的匿名存取驗證
│
├── security/               # 資安不變式與回歸
│   ├── test_settings_hardening.py  # 設定層（讀的是正式設定模組）
│   ├── test_authentication.py      # 登入／JWT cookie／CSRF／帳號列舉
│   ├── test_password_reset.py      # 忘記密碼流程
│   ├── test_authorization.py       # 提權與越權（IDOR）
│   ├── test_pii_leakage.py         # 個資外洩掃描
│   ├── test_throttling.py          # 節流是否真的接上
│   └── test_repo_hygiene.py        # 密鑰／敏感檔案不得進 repo
│
├── api/                    # 各 app 的功能測試
│   ├── test_member_api.py
│   ├── test_company_and_product_api.py
│   ├── test_article_api.py
│   ├── test_recruit_api.py
│   ├── test_picture_api.py
│   ├── test_info_api.py
│   ├── test_contact_and_seo.py
│   └── test_record_monitoring.py
│
├── test_migrations.py      # migration 狀態
└── test_performance_budget.py  # N+1 查詢預算
```

---

## 常用指令

```bash
make test          # 全部（隨機順序）
make security      # 只跑資安測試
make contract      # 只跑 API 契約測試
make perf          # 只跑 N+1 測試
make cov           # 覆蓋率（低於 .coveragerc 的 fail_under 會失敗）
make lint          # 語法／未定義名稱檢查
make check         # Django check + migration check
make audit         # 相依套件 CVE + bandit 靜態掃描
make baseline      # 重新產生路由契約基準檔
make ci            # CI 跑的完整流程
```

單獨執行：

```bash
pytest tests/security/test_authentication.py -v
pytest -k "pii" -v
pytest -m "security and not slow"
```

---

## 測試順序是隨機的

`pytest-randomly` 讓每次執行的順序都不同，用來暴露「測試 A 必須先跑，測試 B 才會過」
這類隱性依賴。要重現某次失敗：

```bash
pytest -p no:randomly              # 固定為檔案順序
pytest --randomly-seed=<失敗時輸出的 seed>
```

---

## 測試不會碰外部世界

`tests/conftest.py` 有三道 autouse 防護，新寫的測試自動受保護：

1. **封鎖對外連線**——loopback 以外的 TCP 連線一律拋 `OutboundNetworkBlocked`。
   看到這個例外表示某段程式碼在測試中打了真實網路，請把它 mock 掉，不要放寬防線。
2. **攔截寄信**——`apps.notice.email.send_email_resend` 被換成記錄器；
   用 `sent_emails` 夾具就能斷言寄了什麼給誰。
3. **清空快取**——`slides_active_v1` 這類 300 秒快取活在整個 pytest 行程裡，
   不清會跨測試污染，症狀是「單獨跑會過、整批跑就掛」。

另外，測試設定拿掉了 `MonitoringMiddleware`、關閉了全域節流。兩者都各有專屬測試
（`api/test_record_monitoring.py`、`security/test_throttling.py`）明確開啟後驗證。

---

## 身分夾具

對應本專案四種權限層級。**寫測試請用夾具，不要自己 `create_user`**，
否則權限層級的定義會散落各處，權限模型一改就得改幾十個檔案。

| 夾具 | 身分 |
|---|---|
| `anon_client` | 未登入 |
| `member_client` | 一般會員 |
| `staff_client` | `is_staff=True` |
| `super_client` | `is_superuser=True` |
| `clients` | 上述四種的對照表（寫權限矩陣用） |

搭配的使用者物件：`member_user` / `other_member_user` / `staff_user` / `super_user`，
資料夾具：`member` / `other_member` / `company` / `industry` / `position`。

工廠拿得到明文密碼：`member_user.raw_password`，可直接拿去打登入端點。

---

## API 契約基準檔

`tests/contracts/routes_baseline.json` 記錄了全部 220 條路由的 URL、HTTP 動詞、
view class、permission class、authentication class 與節流 scope。

**它會失敗，是設計如此。** 流程：

1. 讀失敗訊息列出的差異，確認每一項都是你刻意做的。
2. 是刻意的 → `make baseline`，把產生的 diff 一起提交。
   那份 diff 就是「這次改動對外部介面與權限造成什麼影響」的完整說明。
3. 不是刻意的 → 恭喜，測試抓到 bug 了。

---

## 加新測試

放哪裡：

- 新端點的功能 → `tests/api/test_<app>_api.py`
- 「某某人不該能做某事」 → `tests/security/`
- 列表端點 → 順手在 `tests/test_performance_budget.py` 加一條 N+1 守衛

建資料一律走 `tests/factories.py`。工廠的預設值刻意保守（`is_show=False`、
`active=False`），要公開的測試自己標明 `is_show=True`——這樣「公開端點外洩非公開
資料」的 bug 才會被測出來，而不是被寬鬆的預設值蓋掉。

寫斷言訊息時，寫清楚**為什麼這件事重要**，不要只寫「應該是 200」。
半年後看到紅燈的人（可能是外部貢獻者）需要能直接從訊息判斷嚴重性。

---

## 已知缺陷（`xfail`）

用 `@pytest.mark.xfail(strict=True)` 標記的測試代表「已知的 bug，目前預期會失敗」。
`strict=True` 的意思是**修好之後測試會轉為 XPASS 而讓 CI 失敗**——那正是提醒
「bug 修好了，把 xfail 標記拿掉」的機制，避免修好的問題被無聲遺忘。

目前登記在案的（每一條的 `reason` 都寫了成因與修法）：

| 位置 | 問題 |
|---|---|
| `api/test_recruit_api.py` | 沒有聯絡人的職缺會讓徵才模組前後台全部 500 |
| `api/test_member_api.py` | 登入後自行修改密碼未做強度驗證 |
| `api/test_company_and_product_api.py` | 重複的產品類別名稱回 500 而非 400 |
| `api/test_record_monitoring.py` | 含圖片欄位的模型更新時，稽核記錄靜默失敗 |

---

## 覆蓋率

門檻在 `.coveragerc` 的 `fail_under`（目前 55%）。

覆蓋率是**下限**，不是目標。這套測試的價值集中在契約、資安與效能守衛上——
那些測試涵蓋的程式碼行數不多，抓到的問題卻最貴。不要為了衝數字去寫
「呼叫一次然後 assert 沒爆炸」的測試。

調高門檻時請連同 `.github/workflows/ci.yml` 一起確認，不要只改一邊。
