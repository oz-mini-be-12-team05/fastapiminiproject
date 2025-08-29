# Makefile — FastAPI + uvicorn + 이식용(deps bundle)
#
# ▶ 자주 쓰는 명령
#   - 서버(개발):          make dev
#     (직접 명령)          uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
#   - 서버(프로덕션):      make prod WORKERS=4 HOST=0.0.0.0 PORT=8000
#     (직접 명령)          uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
#   - 패키지 설치(온라인):  make install         # == uv sync
#     (직접 명령)          uv sync
#   - 의존성 묶기(배포용):  make deps-bundle     # requirements.txt + wheelhouse.zip 생성
#   - 패키지 설치(오프라인):
#       unzip wheelhouse.zip && make offline-install   # uv 사용
#       또는  make pip-offline-install                 # pip만 있을 때
#
# ▶ Windows 팁
#   - make 가 없으면 Scoop/Choco로 설치하거나 MSYS2, WSL 사용
#   - MinGW 설치면 `make` 대신 `mingw32-make`
#   - uvicorn 인식 안 되면 아래 UVICORN 줄을 python -m uvicorn 으로 변경
#
# ▶ 변수 오버라이드 예시
#   make dev HOST=0.0.0.0 PORT=9000
#   make prod WORKERS=8

.PHONY: run dev prod clean help install install-no-dev deps-lock deps-export deps-download deps-bundle offline-install pip-offline-install

# ---- 실행 설정 ----
UVICORN ?= uvicorn
# UVICORN ?= python -m uvicorn   # uvicorn 명령 인식 안 되면 이 줄 쓰세요
APP     ?= app.main:app
HOST    ?= 127.0.0.1
PORT    ?= 8000
WORKERS ?= 2

# ---- 도구 ----
UV ?= uv
PY ?= python

help: ## 타깃 설명 보기
	@awk -F':.*?## ' '/^[a-zA-Z0-9_.-]+:.*?## /{printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

run: dev ## alias

# dev: uvicorn app.main:app --reload --host $(HOST) --port $(PORT)
dev: ## 개발 서버(자동 리로드)
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

# prod: uvicorn app.main:app --host $(HOST) --port $(PORT) --workers $(WORKERS)
prod: ## 프로덕션(리로드 없음, 워커 n개)
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --workers $(WORKERS)

clean: ## 캐시 정리
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .ruff_cache wheelhouse wheelhouse.zip

# ---- 패키지 설치 / 이식 ----

# install: uv sync
install: ## 패키지 설치(온라인) — pyproject.toml/uv.lock 기준
	$(UV) sync

# install-no-dev: uv sync --no-dev
install-no-dev: ## dev 그룹 제외 설치
	$(UV) sync --no-dev

# deps-lock: uv lock
deps-lock: ## 잠금파일 생성/갱신(uv.lock)
	$(UV) lock

# deps-export: uv export -o requirements.txt
deps-export: ## requirements.txt 내보내기(고정 버전)
	$(UV) export -o requirements.txt

# deps-download: uv pip download -r requirements.txt -d wheelhouse
deps-download: deps-export ## 의존성 휠만 다운로드(설치 X)
	$(UV) pip download -r requirements.txt -d wheelhouse

# deps-bundle: zip 묶기 (requirements.txt + wheelhouse.zip)
deps-bundle: deps-download ## 다른 PC로 전달용 번들 만들기
	$(PY) -c "import shutil; shutil.make_archive('wheelhouse', 'zip', 'wheelhouse'); print('=> 생성: requirements.txt, wheelhouse.zip')"

# offline-install: uv pip install --no-index --find-links=wheelhouse -r requirements.txt
offline-install: ## 오프라인 설치(uv 사용)
	$(UV) pip install --no-index --find-links=wheelhouse -r requirements.txt

# pip-offline-install: python -m pip install --no-index --find-links=wheelhouse -r requirements.txt
pip-offline-install: ## 오프라인 설치(pip만 있을 때)
	$(PY) -m pip install --no-index --find-links=wheelhouse -r requirements.txt
