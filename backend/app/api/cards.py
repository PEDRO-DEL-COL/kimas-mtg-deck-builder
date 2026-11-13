from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.card import Card
from app.schemas.card import CardDetail, CardPage, CardSummary
from app.services.card_search import (
    CardSearchParams,
    ColorMode,
    InvalidSearchError,
    SortKey,
    search_cards,
)

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("", response_model=CardPage)
def list_cards(
    db: Annotated[Session, Depends(get_db)],
    q: str | None = None,
    identity: str | None = None,
    identity_mode: ColorMode = "subset",
    colors: str | None = None,
    colors_mode: ColorMode = "subset",
    type: str | None = None,
    subtype: str | None = None,
    cmc_min: float | None = None,
    cmc_max: float | None = None,
    text: str | None = None,
    rarity: str | None = None,
    commander_legal: bool | None = None,
    sort: SortKey = "name",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 24,
) -> CardPage:
    params = CardSearchParams(
        q=q,
        identity=identity,
        identity_mode=identity_mode,
        colors=colors,
        colors_mode=colors_mode,
        type=type,
        subtype=subtype,
        cmc_min=cmc_min,
        cmc_max=cmc_max,
        text=text,
        rarity=rarity,
        commander_legal=commander_legal,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    try:
        cards, total = search_cards(db, params)
    except InvalidSearchError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return CardPage(
        items=[CardSummary.model_validate(c) for c in cards],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{card_id}", response_model=CardDetail)
def get_card(card_id: str, db: Annotated[Session, Depends(get_db)]) -> CardDetail:
    card = db.get(Card, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return CardDetail.model_validate(card)
