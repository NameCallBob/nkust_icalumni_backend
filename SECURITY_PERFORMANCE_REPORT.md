# 後端資安審查與效能提升報告

日期：2026-06-27　範圍：`IC_alumni` Django 5.0 後端
環境：全新環境、MySQL 8.0（Docker `hris-local-mysql`，資料庫 `nkust_icalumni`）、Redis（Docker）

---

## 一、環境建置與驗證

| 項目 | 內容 |
|------|------|
| Python | 重建 `venv-alumni`（Python 3.12，原 venv 為他架構無法執行） |
| 套件 | 依 `req.txt` 安裝（mysqlclient 以 Homebrew mysql-client 編譯） |
| 資料庫 | Docker MySQL 內建立 `nkust_icalumni` + 使用者 `bob`；`.env` 之 `SERVER_IP` 由 `localhost` 改 `127.0.0.1`（走 TCP 而非 socket） |
| Migration | 全數套用成功（修正 `record.0001` 之 `PopularQueries.query` 由 `TextField(unique=True)` → `CharField(255)`，MySQL 無法對 TEXT 建唯一索引） |
| Seed | 新增可重複執行的管理命令 `python manage.py seed_demo`（5 會員＋公司＋產品＋文章＋招募＋輪播＋傑出系友/校友＋Info），執行期間關閉寄信避免卡住 |
| 啟動 | `runserver --noreload`（autoreload 會觸發 numpy import 遞迴錯誤） |

**測試帳號**：管理員 `admin@demo.local`／一般會員 `alice@demo.local`～，密碼皆 `Demo#1234`。

---

## 二、原有功能測試與修復

| 問題 | 位置 | 修復 |
|------|------|------|
| `sitemap.xml` 一律 500 | `apps/seo/views.py` | `recruit.update_at`（不存在）→ `recruit.release_date` |
| 入會需求 v2 `detail` 一律 500 | `apps/Info/views.py` | action 方法名 `detail` 與 DRF `ViewSet.detail`(bool) 衝突 → 改名 `detail_view` 並 `url_path="detail"` |
| `search_members` 的 `is_show` 篩選錯誤 | `apps/member/models.py` | `Q(is_show=is_active)` → `Q(is_show=is_show)` |

**回歸測試**：傑出校友單元測試 **29/29 全通過（100%）**；公開讀取／認證／權限阻擋共 28 項全部符合預期。

---

## 三、資安審查與修補

> 全域 `DEFAULT_PERMISSION_CLASSES = AllowAny`，權限採「逐端點 opt-in」，是多數問題根因。

### Critical（已驗證可利用、已修補）
- **CRIT-1 權限提升**：未驗證者可透過 `POST /basic/register` 帶 `position.title="管理員"` 直接成為 Django superuser。**實測確認可利用**。
  → 移除 `MemberSerializer.check_and_set_superuser` 及其呼叫；權限不可由前端 position 推導。
- **CRIT-2 個資外洩 / IDOR**：`/member/logined/getOne/` 為 `AllowAny`，可列舉任意會員電話/地址/生日/Email。
  → 改為需登入（`IsAuthenticated`）。
- **CRIT-3 空密碼帳號**：Excel 批次匯入以 `password=""` 建帳號，`authenticate(password="")` 會成功（認證繞過）。
  → 改為產生 12 碼隨機密碼。

### High（已修補）
- **HIGH-1 重設碼暴力破解**：6 位數重設碼未綁定 email、無嘗試限制 → 可接管任意帳號。
  → 確認時必須帶 email 綁定帳號＋新密碼強度驗證＋單次使用；產碼改用 `secrets`；加上 `password_reset` 節流。
- **HIGH-2 IDOR**：product / picture(self/company/product) / recruit 的改/刪未驗證擁有者。
  → 全部加上 `company__member=request.user.member` 等擁有者過濾，非擁有者回 404（實測 alice 無法刪 bob 產品）。
- **HIGH-3 內容越權**：文章、首頁輪播任何會員可增改刪。
  → 改為 `IsStaffPermission`（管理員）。
- **HIGH-4 未驗證刪除畢業資料**：`graduate/remove` 無權限類別 → 落到 AllowAny，且 O2O CASCADE 連帶刪會員。
  → 改為管理員限定（同時加固 `position/remove`）。
- **HIGH-5 明文密碼入庫**：監控中介層把登入/改密請求 body（含明文密碼）寫入 `RequestLog`。
  → 新增 `_redact_sensitive`，遮罩 password/code/token 等欄位。

### Medium（已修補）
- **MED-1 Mass assignment**：公司自助更新可改 `clicks`/`created_at` → 設為 `read_only`。
- **MED-2 CORS 失效**：`corsMiddleForStatic` 對「所有」回應加 `ACAO:*` → 限縮為僅 `/static/`、`/media/`。
- **MED-4 缺乏防爆破節流**：新增 `login 10/min`、`password_reset 5/min`、`register 10/hour` 範圍節流。
- **INFO-1**：移除指向不存在 `data_maintenance.serializers` 的死設定（避免日後接 `TokenObtainPairView` 時 import 500）。

### 仍建議後續處理（未在本次修補）
- 正式環境應**輪換** `.env` 內所有密鑰（SECRET_KEY 同時是 JWT 簽章金鑰）、改用 secrets manager。
- 升級／替換 **CKEditor 4**（已知安全問題，Django check 持續警告）。
- MED-3 帳號列舉（登入/重設回應訊息可區分）、MED-5 明文密碼寄信、MED-6 媒體檔公開可猜路徑、INFO-2 base64 上傳缺型別/大小驗證、INFO-3 移除 `print` 除錯輸出。
- 結構性建議：將全域預設權限改為 `IsAuthenticated`，再對公開端點明確標註 `AllowAny`，可根除「忘了加權限」這類問題。

---

## 四、效能提升

| 項目 | 修補 | 效果 |
|------|------|------|
| **H1 GeoIP** | `utils/get_ip.py` 改為整程序單一 Reader（原每請求 open/parse/close mmdb） | 監控中介層最大單筆開銷消除 |
| **H3 傑出系友/校友** | viewset queryset 補 `select_related('member','member__position','member__graduate')` | featured 端點 **7 → 1 查詢**（實測，N+1 消除） |
| **H4 公司首頁三組件** | mostView/newUpload/randomCompanies 補 `select_related` | 首頁約省 ~40 查詢 |
| **H5/H6 公司列表** | 公開/管理列表補 `member__graduate`、`member__position` | 列表 N+1 消除 |
| **H7/H8 會員列表** | `search_members`、`tableOutput_all` 補 `select_related` | 每列 5 查詢 → 常數 |
| **M1 索引** | 新增 11 個索引（傑出系友/校友 is_featured+sort_order、recruit.active、product(company,is_active)、slide(active,priority)、popup.active、private.is_active），並把先前 migration 已建但模型未宣告的索引補回模型使狀態一致 | 熱門篩選/排序加速 |
| **M2 快取** | 首頁輪播 `slide-images/active` 加 Redis 快取（300s）＋ 寫入時失效 | 高流量公開端點減少 DB 查詢 |
| **L3 批次排序** | `batch_update_sort_order` 逐筆 save → `bulk_update` | 多次 UPDATE → 單次 |

**後續建議**：可比照 M2 為 popup-ads、傑出校友 featured、Info latest、公司 mostView 等公開讀取端點加入短 TTL 快取；監控中介層的逐請求 `RequestLog` 寫入與 `IPLimit` 查詢建議改採樣或移至 Redis 計數。

---

## 四之二、第二輪修復（技術債清理）

| 項目 | 內容 | 影響前端？ |
|------|------|-----------|
| IsStaffPermission | 放寬為 `is_staff or is_superuser`，避免歷史上僅有 superuser 的管理員被鎖死 | 否 |
| 公司 member 綁定（IDOR） | `company/new` 由伺服器端綁定 `request.user` 的 member（忽略前端傳入）；`member` 設為序列化器唯讀，`selfChange` 無法把公司改綁他人。已實測：帶 `member:1` 仍綁定自己 | 否（路徑/格式不變） |
| 監控中介層效能 | ① IP 封鎖狀態快取 60s（免每請求查 DB）② 請求計數改背景非阻塞 ③ `response_size` 改用 Content-Length（不強制渲染/破壞串流）。已實測：連續請求 31ms→5ms，IP 計數仍正常累加 | 否 |
| 移除 print | 清掉 14 處散落的 `print()` 除錯輸出（recruit 序列化器×12、member/picture views×2） | 否 |
| 登入防帳號列舉（MED-3） | 先驗密碼再判停用；帳號不存在/密碼錯誤/停用帶錯密碼一律回 400，僅「密碼正確但停用」回 403（保留前端既有 UX）。已實測 5 種情境符合 | 否（403 UX 保留） |

> 前端比對：改權限的端點（文章/輪播/職位管理）皆只在前端 `Manager/` 後台呼叫，且後端原本就有 63 處 `IsAdminUser`（同需 is_staff），故與既有權限模型一致。`logined/getOne` 前端未使用。IDOR 修補後已實測合法擁有者仍可操作自己的資料。

## 四之三、第三輪修復（上傳驗證 + 媒體保護）

| 項目 | 內容 | 影響前端？ |
|------|------|-----------|
| 共用 Base64ImageField（INFO-2） | 新增大小上限（預設 5MB，可由 `settings.MAX_IMAGE_UPLOAD_SIZE` 覆寫）、以「實際內容」嗅探型別並限白名單（jpg/png/gif/webp）、未知型別一律拒絕（原本未知會預設存成 jpg）。涵蓋 recruit/picture/product/company/article。已單元測試：合法 PNG 接受、偽裝非圖片拒絕、超大檔拒絕 | 否（合法圖片照常接受） |
| Info 圖片欄位（INFO-2） | Info 自有 Base64 欄位同樣加上大小/內容型別驗證、不再信任前端宣稱的副檔名；**保留 to_representation 既有 base64 讀取行為**避免影響前端 | 否 |
| Excel 預覽媒體外洩（MED-6） | 含會員 Email 的 Excel **不再寫入** web 可服務的 `MEDIA_ROOT/member_preview`（原檔名可預測且永久殘留），改為記憶體解析；加副檔名（.xlsx/.xls）與 5MB 大小檢查。**並清除了既存的殘留檔** `預覽上傳_20250613_135500.xlsx` | 否（回傳格式不變） |
| 缺漏相依 openpyxl | 補裝 `openpyxl`（pandas 讀 .xlsx 必需，原 env 缺少導致 Excel 匯入功能實際無法運作），並加入 `req.txt` | — |

> 已實測：管理員以合法圖片建立輪播圖成功（檔名為隨機 uuid）、Excel 預覽正確回傳每筆 Email 狀態且不再於 media 目錄產生檔案、非 Excel 檔上傳回 400。

## 四之四、權限模型改為「預設拒絕」（結構性資安修補）

將全域 `DEFAULT_PERMISSION_CLASSES` 由 `AllowAny` 改為 `IsAuthenticated`，從「預設開放、逐一保護」翻轉為「預設拒絕、逐一開放」，根除「忘了加權限」造成的未授權存取。

**做法（先盤點公開頁面端點再翻轉）**：
1. 掃描前端所有「免登入頁面」（首頁、搜尋、系友列表/介紹、招募、聯絡、IC 簡介/章程/組織/入會、登入、忘記密碼）及其子元件，列出實際呼叫的 **34 個公開端點**。
2. 確認每個公開端點在後端皆已明確標註 `AllowAny` 或 `permission_classes=[]`（靜態檢查 + 匿名實測）。
3. 翻轉全域預設為 `IsAuthenticated`。

**驗證結果**：
- 33 個可測公開端點翻轉後仍可匿名存取（0 個被權限擋下）。
- 受保護端點匿名存取已正確回 401（`member/logined/selfInfo/`、`member/admin/tableOutput_all/`、`api/monitoring/requests/`）。
- 帶 token 的會員/管理員流程全部正常（200）。
- 靜態確認：**無任何端點**同時「停用驗證（`authentication_classes=[]`）」又「未明確設定權限」，故翻轉不會誤傷公開流程。
- 前端匿名請求送出的 `Authorization: None` 由 SimpleJWT 視為匿名，不影響公開端點。

**過程中發現的前後端不一致與處置**：
- `POST record/contact/`（聯絡我們表單）：原本後端**無此路由**（record 掛在 `api/monitoring/`，且舊 `ContactForm` model/資料表已被刪除）→ **已實作**：新增 `ContactMessage` model + migration + 公開且節流（20/hour）的 `ContactCreateView`，路由掛在 `record/contact/`，並註冊 Django admin 供管理員檢視/標記處理。已實測匿名送出 201、缺欄位 400、資料正確入庫。
- `GET basic/check-user`（登入頁 Email 預檢）：**決定不實作**。該端點本質是「確認某 Email 是否註冊並回傳姓名」，等同對匿名者開放帳號列舉 + 個資外洩，會抵銷 MED-3 的修補。前端已對 404 做 graceful catch（改顯示通用歡迎詞並照常進入密碼階段），登入流程不受影響；建議前端移除此呼叫。
- `company/search/` 傳入非數字 industry 會 500 → 已加數字守衛修正（前端實際送數字 id，正常情況不受影響）。

## 四之五、聯絡端點 + MED-5（明文密碼寄信）

| 項目 | 內容 |
|------|------|
| 聯絡我們端點 | 新增 `ContactMessage` model/migration、公開節流（20/hour）`ContactCreateView`、路由 `record/contact/`、Django admin 檢視。實測匿名 201、缺欄位 400、入庫正確 |
| MED-5 明文密碼寄信 | `welcome.html` 移除 `{{password}}`，改引導使用者用「忘記密碼」設定密碼；`member_account_created` 不再注入 password。涵蓋三條建立帳號路徑（自助註冊、Excel 批次匯入、管理員建立），全部不再寄送明文密碼 |
| basic/check-user | 決定不實作（會造成帳號列舉/個資外洩），前端對 404 已 graceful 處理 |

## 四之六、前端畫面配合後端機制（frontend alignment）

後端契約有變動之處，已同步調整前端（檔案均通過 JSX 語法驗證）：

| 後端機制變動 | 前端調整 | 檔案 |
|------|------|------|
| **HIGH-1 密碼重設需綁定 email**（不送 email 會 400） | 重設請求改為一併送 `email`；錯誤訊息支援後端 `error`（字串/陣列，如密碼強度）顯示 | `ResetPassPage.js` |
| **MED-5 不再寄送明文密碼** | 後台「僅輸入 Email 建立帳號」成功後提示「請通知使用者用忘記密碼設定密碼」，並於表單加入永久說明 | `NewUserModal.js` |
| **basic/check-user 不提供（防帳號列舉）** | 移除登入頁對 check-user 的呼叫，直接進入密碼階段顯示通用歡迎詞 | `LoginPage.js` |
| **登入節流 429（10 次/分）** | 依 `Retry-After` 標頭設定冷卻倒數並提示 | `LoginPage.js` |
| **record/contact/ 端點已實作** | 既有聯絡表單送出即可正常運作（201 成功提示），無需改動 | `ContactUsPage.js`（驗證無誤） |

> 已用後端實測驗證重設流程：不送 email → 400（舊前端行為會壞）、送 email → 200、再以新密碼登入 → 200，證實前端調整為必要且正確。

## 五、如何重現

```bash
cd IC_alumni
# 1) 啟動 docker MySQL/Redis（既有），確認 nkust_icalumni 資料庫存在
# 2) 套用 schema 與 seed
DJANGO_SETTINGS_MODULE=IC_alumni.settings ./venv-alumni/bin/python manage.py migrate
DJANGO_SETTINGS_MODULE=IC_alumni.settings ./venv-alumni/bin/python manage.py seed_demo
# 3) 啟動
DJANGO_SETTINGS_MODULE=IC_alumni.settings ./venv-alumni/bin/python manage.py runserver 127.0.0.1:8001 --noreload
```
