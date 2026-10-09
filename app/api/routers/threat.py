from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.threat import (
    QrThreatRequest,
    SmsThreatRequest,
    ThreatEventDetailResponse,
    ThreatEventResponse,
    ThreatEventSummaryResponse,
    ThreatImpactResponse,
    ThreatSignalResponse,
    UrlThreatRequest,
)
from app.contracts.events import ThreatChannel, ThreatEvent
from app.models.tables import User
from app.modules.threat.call_analyzer import transcribe_audio
from app.modules.threat.impact import ThreatImpact
from app.modules.threat.service import ThreatService
from app.platform.database import get_session
from app.platform.deps import get_current_user

router = APIRouter(prefix="/threat", tags=["threat"])


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


def _to_impact_response(impact: ThreatImpact | None) -> ThreatImpactResponse | None:
    if impact is None:
        return None
    return ThreatImpactResponse(
        would_cause_shortfall=impact.would_cause_shortfall,
        prob_before=impact.prob_before,
        prob_after=impact.prob_after,
        obligations_at_risk=impact.obligations_at_risk,
        days_until_first_impact=impact.days_until_first_impact,
        human_statement=impact.human_statement,
    )


def _to_event_response(threat: ThreatEvent, impact: ThreatImpact | None) -> ThreatEventResponse:
    return ThreatEventResponse(
        threat_id=threat.threat_id,
        channel=threat.channel.value,
        risk_score=threat.risk_score,
        primary_category=threat.primary_category.value,
        signals=[
            ThreatSignalResponse(
                name=signal.name,
                category=signal.category.value,
                weight=signal.weight,
                evidence=signal.evidence,
                detector=signal.detector,
            )
            for signal in threat.signals
        ],
        requested_amount=threat.requested_amount,
        payee_identifier=threat.payee_identifier,
        detected_at=threat.detected_at,
        impact=_to_impact_response(impact),
    )


@router.post("/sms", response_model=ThreatEventResponse)
async def analyse_sms_threat(
    payload: SmsThreatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ThreatEventResponse:
    result = await ThreatService().analyse(
        session,
        current_user.id,
        ThreatChannel.sms,
        {"body": payload.body, "sender": payload.sender},
        trace_id=_trace_id(request),
    )
    return _to_event_response(result.threat, result.impact)


@router.post("/url", response_model=ThreatEventResponse)
async def analyse_url_threat(
    payload: UrlThreatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ThreatEventResponse:
    result = await ThreatService().analyse(
        session, current_user.id, ThreatChannel.link, {"url": payload.url}, trace_id=_trace_id(request)
    )
    return _to_event_response(result.threat, result.impact)


@router.post("/qr", response_model=ThreatEventResponse)
async def analyse_qr_threat(
    payload: QrThreatRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ThreatEventResponse:
    result = await ThreatService().analyse(
        session,
        current_user.id,
        ThreatChannel.qr,
        {"qr_payload": payload.qr_payload, "claimed_merchant_name": payload.claimed_merchant_name},
        trace_id=_trace_id(request),
    )
    return _to_event_response(result.threat, result.impact)


@router.post("/call", response_model=ThreatEventResponse)
async def analyse_call_threat(
    request: Request,
    # multipart form (not a JSON body) so this one endpoint can accept
    # EITHER a typed/simulated transcript OR an uploaded audio recording.
    transcript: str | None = Form(None),
    audio: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ThreatEventResponse:
    if transcript is None and audio is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provide either transcript or audio"
        )

    resolved_transcript = transcript
    if resolved_transcript is None and audio is not None:
        with tempfile.NamedTemporaryFile(suffix=Path(audio.filename or "audio").suffix, delete=False) as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name
        try:
            transcription = await transcribe_audio(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        if not transcription.available or transcription.text is None:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=transcription.reason or "Audio transcription is unavailable",
            )
        resolved_transcript = transcription.text

    result = await ThreatService().analyse(
        session, current_user.id, ThreatChannel.call, {"transcript": resolved_transcript}, trace_id=_trace_id(request)
    )
    return _to_event_response(result.threat, result.impact)


@router.get("/events", response_model=list[ThreatEventSummaryResponse])
async def list_threat_events(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ThreatEventSummaryResponse]:
    rows = await ThreatService().get_events(session, current_user.id)
    return [ThreatEventSummaryResponse.model_validate(row) for row in rows]


@router.get("/events/{threat_id}", response_model=ThreatEventDetailResponse)
async def get_threat_event(
    threat_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ThreatEventDetailResponse:
    row = await ThreatService().get_event(session, current_user.id, threat_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threat event not found")
    return ThreatEventDetailResponse.model_validate(row)
