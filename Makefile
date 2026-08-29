# IC_alumni 後端開發指令。
#
# 所有測試皆為離線執行：SQLite in-memory、locmem 郵件、封鎖對外連線。
# 不需要 MySQL、Redis，也不會寄出任何郵件。

PYTHON ?= ./venv-alumni/bin/python
PYTEST := $(PYTHON) -m pytest
# CI 與本機都需要一個 SECRET_KEY 才能匯入設定；測試用的假值，不對應任何環境。
export SECRET_KEY ?= local-test-secret-key-not-for-production

.DEFAULT_GOAL := help
.PHONY: help install test test-fast security contract perf cov cov-html lint audit baseline check ci clean

help:  ## 顯示可用指令
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## 安裝正式與開發相依套件
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

test:  ## 跑全部測試（隨機順序）
	$(PYTEST)

test-fast:  ## 跑全部測試，跳過標記為 slow 的
	$(PYTEST) -m "not slow"

security:  ## 只跑資安相關測試
	$(PYTEST) -m security

contract:  ## 只跑 API 契約測試（路由清單／權限矩陣）
	$(PYTEST) -m contract

perf:  ## 只跑查詢預算（N+1）測試
	$(PYTEST) -m performance

cov:  ## 跑測試並輸出覆蓋率（低於門檻會失敗）
	$(PYTEST) --cov --cov-report=term-missing --cov-report=xml

cov-html:  ## 產生 HTML 覆蓋率報告至 reports/coverage-html/
	$(PYTEST) --cov --cov-report=html
	@echo "報告：reports/coverage-html/index.html"

lint:  ## 只抓會炸的問題（語法錯誤、未定義名稱）
	$(PYTHON) -m flake8 . --select=E9,F63,F7,F82 \
		--exclude=venv-alumni,migrations,static,static_files,system_needed,node_modules

audit:  ## 掃描相依套件的已知弱點與原始碼的常見資安問題
	$(PYTHON) -m pip_audit -r requirements.txt --desc || true
	$(PYTHON) -m bandit -r apps IC_alumni utils -ll --exclude '*/migrations/*' || true

baseline:  ## 重新產生 API 路由契約基準檔（介面刻意變動時才執行）
	$(PYTHON) -m tests.contracts.update_baseline

check:  ## Django 系統檢查 + 缺漏 migration 檢查
	$(PYTHON) manage.py check
	$(PYTHON) manage.py makemigrations --check --dry-run

ci: lint check cov  ## CI 跑的完整流程

clean:  ## 清除測試產物
	rm -rf reports .pytest_cache .coverage coverage.xml
	find . -path ./venv-alumni -prune -o -name '__pycache__' -type d -print0 | xargs -0 rm -rf
