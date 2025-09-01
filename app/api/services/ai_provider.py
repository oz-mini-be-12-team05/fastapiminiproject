# app/api/services/ai_provider.py
from __future__ import annotations
import os, json, re
from typing import Protocol, Tuple, List, Any
from collections import Counter
import anyio

try:
    import google.generativeai as genai
except Exception:
    genai = None  # 미설치 대비

# ---- 인터페이스 --------------------------------------------------------------
class AIProvider(Protocol):
    async def summarize(self, title: str, content: str, max_sentences: int = 2) -> str: ...
    async def analyze(self, text: str) -> Tuple[str, List[str]]: ...

# ---- Rule-based 폴백(키 없거나 에러 시) --------------------------------------
class RuleBasedAI(AIProvider):
    POS = {"좋다","행복","기쁨","즐거","멋지","사랑","행운","훌륭","awesome","great","good","love"}
    NEG = {"나쁘","화남","짜증","우울","불안","실망","슬픔","싫다","terrible","bad","hate"}

    async def summarize(self, title: str, content: str, max_sentences: int = 2) -> str:
        text = f"{title}. {content}".strip()
        sents = re.split(r"(?<=[.!?。！？])\s+", text)
        return " ".join(sents[:max_sentences])[:400]

    async def analyze(self, text: str):
        words = re.findall(r"[A-Za-z가-힣0-9#@]+", text.lower())
        cnt = Counter(w for w in words if len(w) > 1)
        score = sum(+1 for w in cnt if w in self.POS) - sum(1 for w in cnt if w in self.NEG)
        emo = "positive" if score > 0 else "negative" if score < 0 else "neutral"
        keywords = [w for w, _ in cnt.most_common(3)]
        return emo, keywords

# ---- Gemini 구현 ------------------------------------------------------------
class GeminiAI(AIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        if genai is None:
            raise RuntimeError("google-generativeai가 설치되지 않았습니다.")
        genai.configure(api_key=api_key)
        # 텍스트/JSON 응답을 분리해 안정성 ↑
        self.model_text = genai.GenerativeModel(
            model_name,
            generation_config={
                "temperature": 0.6,      # 과하지 않게
                "top_p": 0.9,
                "max_output_tokens": 512,
            },
        )
        self.model_json = genai.GenerativeModel(
            model_name,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2,     # 분류/추출은 낮게
                "max_output_tokens": 256,
            },
        )

    async def _gen_text(self, prompt: str) -> str:
        def _call():
            resp = self.model_text.generate_content(prompt)
            return getattr(resp, "text", "").strip()
        return await anyio.to_thread.run_sync(_call)

    async def _gen_json(self, prompt: str) -> dict[str, Any]:
        def _call():
            resp = self.model_json.generate_content(prompt)
            return json.loads(getattr(resp, "text", "").strip())
        try:
            return await anyio.to_thread.run_sync(_call)
        except Exception:
            # 가끔 텍스트/마크다운 섞여 나오는 경우 대비
            def _call2():
                resp = self.model_text.generate_content(prompt)
                txt = getattr(resp, "text", "")
                m = re.search(r"\{.*\}", txt, flags=re.S)
                return json.loads(m.group(0)) if m else {}
            return await anyio.to_thread.run_sync(_call2)

    async def summarize(self, title: str, content: str, max_sentences: int = 2) -> str:
        prompt = (
            "당신은 일기를 한국어로 깔끔하게 요약하는 비서입니다.\n"
            f"- 최대 {max_sentences}문장으로 요약하세요.\n"
            "- 핵심 사실/행동/감정만 남기고 군더더기(이모지·말줄임표·반복문장)는 제거합니다.\n"
            "- 1문장은 20~60자 정도로 간결하게.\n"
            f"제목: {title}\n"
            f"내용:\n{content}\n"
        )
        return await self._gen_text(prompt)

    async def analyze(self, text: str):
        prompt = (
            "다음 텍스트의 감정을 분류하고 핵심 키워드를 추출하세요.\n"
            'JSON으로만 응답하세요. 예시 형식: {"emotion":"positive|negative|neutral","keywords":["키워드1","키워드2","키워드3"]}\n'
            "- emotion은 positive/negative/neutral 중 하나만.\n"
            "- keywords: 최대 5개, 2~20자, 중복 제거, 한국어/영어 단어 중심, 특수문자·이모지 제외.\n"
            f"텍스트:\n{text}\n"
        )
        data = await self._gen_json(prompt)
        emo = (data.get("emotion") or "neutral").lower()
        if emo not in {"positive", "negative", "neutral"}:
            emo = "neutral"
        kws = data.get("keywords") or []
        # 후처리(길이/중복/공백)
        out, seen = [], set()
        for k in kws:
            s = str(k).strip()
            if 2 <= len(s) <= 20 and s not in seen:
                seen.add(s); out.append(s)
        return emo, out[:5]

# ---- 팩토리 ------------------------------------------------------------------
def make_ai() -> AIProvider:
    if os.getenv("USE_FAKE_AI", "").lower() in {"1","true","yes"}:
        return RuleBasedAI()
    key = os.getenv("GEMINI_API_KEY")
    if key:
        try:
            return GeminiAI(api_key=key)
        except Exception:
            return RuleBasedAI()
    return RuleBasedAI()

ai: AIProvider = make_ai()
