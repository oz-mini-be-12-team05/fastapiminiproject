# Makefile — FastAPI + uvicorn (plain)
.PHONY: run dev prod clean help

# 실행 커맨드 (윈도우서 'uvicorn' 인식이 안 되면 아래 줄을 주석 해제하고 python -m 사용)
UVICORN ?= uvicorn
# UVICORN ?= python -m uvicorn

APP     ?= app.main:app
HOST    ?= 127.0.0.1
PORT    ?= 8000
WORKERS ?= 2

help: ## 타깃 설명 보기
	@awk -F':.*?## ' '/^[a-zA-Z0-9_.-]+:.*?## /{printf "\033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

run: dev ## alias

dev: ## 개발 서버(자동 리로드)
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

prod: ## 프로덕션(리로드 없음, 워커 n개)
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --workers $(WORKERS)

clean: ## 캐시 정리
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .ruff_cache


#make run 서버실행