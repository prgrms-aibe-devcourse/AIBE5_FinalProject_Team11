"""
Korean NLP templates for elbee.yogaman.club.

Handles 조사 (postpositions) automatically via 받침 (batchim) detection so that
generated copy is grammatically natural regardless of which location name is used.

Usage:
    from app.services.templates import get_template, get_time_trigger

    msg = get_template("morning", location="성수동")
    # → "상쾌한 아침이에요! 🌅 성수동은 근처에서 가볍게..."

    msg = get_template("club_invite", location="강남", studio_name="강남 elbee 스튜디오")
"""
from __future__ import annotations

import datetime
from typing import Dict, Optional


# ── 받침 (batchim) helpers ────────────────────────────────────────────────────

def _has_batchim(word: str) -> bool:
    """True if the last Hangul character has a final consonant (받침)."""
    if not word:
        return False
    ch = word[-1]
    if not ('\uAC00' <= ch <= '\uD7A3'):
        return False          # non-Hangul → assume no batchim (safe default)
    return (ord(ch) - 0xAC00) % 28 != 0


def _batchim_code(word: str) -> int:
    """Return batchim index (0 = vowel ending, 8 = ㄹ ending, etc.)."""
    if not word:
        return 0
    ch = word[-1]
    if not ('\uAC00' <= ch <= '\uD7A3'):
        return 0
    return (ord(ch) - 0xAC00) % 28


# ── Public 조사 functions ──────────────────────────────────────────────────────

def josa_eun_neun(word: str) -> str:
    """은/는  (topic marker)"""
    return "은" if _has_batchim(word) else "는"


def josa_i_ga(word: str) -> str:
    """이/가  (subject marker)"""
    return "이" if _has_batchim(word) else "가"


def josa_eul_reul(word: str) -> str:
    """을/를  (object marker)"""
    return "을" if _has_batchim(word) else "를"


def josa_euro_ro(word: str) -> str:
    """으로/로  (directional / instrumental marker)
       Rule: 로 after vowel or ㄹ, 으로 after other consonants.
    """
    code = _batchim_code(word)
    if code == 0 or code == 8:   # 0 = vowel-ending, 8 = ㄹ
        return "로"
    return "으로"


def josa_wa_gwa(word: str) -> str:
    """와/과  (and / with)"""
    return "과" if _has_batchim(word) else "와"


# ── Template renderer ──────────────────────────────────────────────────────────

def render(template: str, location: str = "", **kwargs) -> str:
    """
    Render a template string with automatic 조사 resolution.

    Supported auto-resolved placeholders (all based on `location`):
      {location}   — location name
      {eun_neun}   — 은/는
      {i_ga}       — 이/가
      {eul_reul}   — 을/를
      {euro_ro}    — 으로/로
      {wa_gwa}     — 와/과

    Any extra kwargs are passed through to str.format() as-is.
    """
    return template.format(
        location=location,
        eun_neun=josa_eun_neun(location) if location else "",
        i_ga=josa_i_ga(location) if location else "",
        eul_reul=josa_eul_reul(location) if location else "",
        euro_ro=josa_euro_ro(location) if location else "",
        wa_gwa=josa_wa_gwa(location) if location else "",
        **kwargs,
    )


# ── Template dictionary ────────────────────────────────────────────────────────

TEMPLATES: Dict[str, str] = {
    # ── Time-of-day triggers ──────────────────────────────────────────────
    "morning": (
        "상쾌한 아침이에요! 🌅 {location}{eun_neun} 근처에서 가볍게 몸을 깨워보는 건 어떨까요? "
        "elbee 파트너 스튜디오가 여러분을 기다리고 있어요."
    ),
    "afternoon": (
        "점심 시간, 잠깐의 스트레칭으로 오후 에너지를 충전해 보세요! ☀️ "
        "{location} 근처 elbee 스팟을 확인해 드릴게요."
    ),
    "evening": (
        "오늘 하루도 수고 많으셨어요. 🌙 퇴근길 {location}{eun_neun} 근처 elbee 스튜디오에서 "
        "요가로 스트레스를 비워내 보세요."
    ),

    # ── Proximity triggers ────────────────────────────────────────────────
    "proximity_club": (
        "현재 {location} 근처에 elbee 공식 파트너 스튜디오{i_ga} 있어요! 🧘 "
        "오늘도 매트 위에 서실 준비 되셨나요? 지금 바로 수련하러 가보실까요?"
    ),
    "proximity_public": (
        "{location}{eun_neun} 멋진 야외 요가 스팟이에요! 🌿 "
        "자연과 함께하는 수련, 오늘 한번 도전해 보시는 건 어떨까요?"
    ),

    # ── Weather-based triggers ────────────────────────────────────────────
    "outdoor_sunny": (
        "오늘 날씨가 맑아요! ☀️ {location} 근처 야외 요가 스팟으로 안내해 드릴게요. "
        "자연 속 수련은 마음까지 맑아지게 한답니다."
    ),
    "rainy_day": (
        "비가 오는 날엔 실내 스튜디오가 제격이죠. 🌧️ "
        "{location} 근처 elbee 파트너 스튜디오를 찾아드릴게요."
    ),

    # ── Club invite (1 km radius hit) ─────────────────────────────────────
    "club_invite": (
        "안녕하세요, elbee 멤버! 🙏 오늘 {location}{eun_neun} 근처 **{studio_name}**에서 "
        "수련하실 기회가 생겼어요. 지금 예약하시면 첫 방문 혜택도 받으실 수 있어요!"
    ),

    # ── Fallbacks ─────────────────────────────────────────────────────────
    "no_result": (
        "현재 위치 근처에 등록된 elbee 스팟을 찾지 못했어요. 🗺️ "
        "하지만 어디서든 매트 하나면 충분하답니다! "
        "새로운 장소를 등록하고 싶으시면 알려주세요."
    ),
    "content_not_found": (
        "해당 내용을 GEO 레퍼런스에서 찾지 못했어요. 🤔 "
        "다른 키워드로 다시 검색해 보시거나, 더 구체적인 질문을 해주세요."
    ),
}


# ── Time helper ───────────────────────────────────────────────────────────────

def get_time_trigger() -> str:
    """Return 'morning', 'afternoon', or 'evening' based on current KST time."""
    kst_hour = (datetime.datetime.utcnow().hour + 9) % 24
    if 5 <= kst_hour < 11:
        return "morning"
    if 11 <= kst_hour < 17:
        return "afternoon"
    return "evening"


def get_template(key: str, location: str = "", **kwargs) -> str:
    """Render a named template with automatic 조사 resolution."""
    tpl = TEMPLATES.get(key, TEMPLATES["no_result"])
    return render(tpl, location=location, **kwargs)
