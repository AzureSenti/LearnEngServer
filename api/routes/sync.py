from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from api.deps import get_current_user
from core.db import get_session
from model.dto.sync import (
    GrammarProgressDownload,
    GrammarProgressUpload,
    SyncDownloadResponse,
    SyncUploadRequest,
    UserProfileDownload,
    WordSrsDownload,
)
from model.entity.user import User
from model.entity.user_grammar_progress import UserGrammarProgress
from model.entity.user_word_set_cross_ref import UserWordSetCrossRef
from model.entity.word import Word
from model.entity.word_set import WordSet
from model.entity.word_set_cross_ref import WordSetCrossRef
from model.entity.word_srs import WordSrs

router = APIRouter(prefix="/sync", tags=["Sync"])


# ---------------------------------------------------------------------------
# Upload – Client pushes unsynced data to the server
# ---------------------------------------------------------------------------


@router.post("/upload")
async def upload_progress(
    request: SyncUploadRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Receive learning progress from the client and merge into PostgreSQL.

    Merge strategy:
    - ``word_srs``: UPSERT – keep the record with the *higher* ``last_review_date``.
    - ``grammar_progress``: UPSERT – keep max score, OR the passed flags.
    - ``unlocked_word_sets``: INSERT IGNORE duplicates.
    - ``user_profile``: keep the higher coins / streak values.
    """
    user_id = current_user.user_id

    # ---- Custom Words ----
    for item in request.words_list:
        existing = session.exec(
            select(Word).where(
                Word.user_id == user_id,
                Word.word_id == item.word_id,
            )
        ).first()

        if existing is None:
            session.add(
                Word(
                    user_id=user_id,
                    word_id=item.word_id,
                    english_word=item.english_word,
                    vietnamese_meaning=item.vietnamese_meaning,
                    audio=item.audio or "",
                )
            )
        else:
            existing.english_word = item.english_word
            existing.vietnamese_meaning = item.vietnamese_meaning
            existing.audio = item.audio or ""
            session.add(existing)

    # ---- Custom Word Sets ----
    for item in request.word_sets_list:
        existing = session.exec(
            select(WordSet).where(
                WordSet.user_id == user_id,
                WordSet.set_id == item.set_id,
            )
        ).first()

        if existing is None:
            session.add(
                WordSet(
                    user_id=user_id,
                    set_id=item.set_id,
                    name=item.name,
                    unlock_cost=item.unlock_cost,
                )
            )
        else:
            existing.name = item.name
            existing.unlock_cost = item.unlock_cost
            session.add(existing)

    # ---- Word Set Cross Refs ----
    for item in request.word_set_cross_refs_list:
        existing = session.exec(
            select(WordSetCrossRef).where(
                WordSetCrossRef.user_id == user_id,
                WordSetCrossRef.word_id == item.word_id,
                WordSetCrossRef.set_id == item.set_id,
            )
        ).first()

        if existing is None:
            session.add(
                WordSetCrossRef(
                    user_id=user_id,
                    word_id=item.word_id,
                    set_id=item.set_id,
                )
            )

    # ---- Word SRS ----
    for item in request.word_srs_list:
        existing = session.exec(
            select(WordSrs).where(
                WordSrs.user_id == user_id,
                WordSrs.word_id == item.word_id,
            )
        ).first()

        if existing is None:
            new_record = WordSrs(
                user_id=user_id,
                word_id=item.word_id,
                level=item.level,
                next_review_date=item.next_review_date,
                last_review_date=item.last_review_date,
            )
            session.add(new_record)
        else:
            # Keep the more recent review
            client_date = item.last_review_date or 0
            server_date = existing.last_review_date or 0
            if client_date >= server_date:
                existing.level = item.level
                existing.next_review_date = item.next_review_date
                existing.last_review_date = item.last_review_date
                session.add(existing)

    # ---- Grammar progress ----
    for item in request.grammar_progress_list:
        existing = session.exec(
            select(UserGrammarProgress).where(
                UserGrammarProgress.user_id == user_id,
                UserGrammarProgress.lesson_id == item.lesson_id,
            )
        ).first()

        if existing is None:
            new_record = UserGrammarProgress(
                user_id=user_id,
                lesson_id=item.lesson_id,
                is_theory_completed=item.is_theory_completed,
                is_quiz_passed=item.is_quiz_passed,
                score=item.score,
            )
            session.add(new_record)
        else:
            # Merge: keep best results
            existing.is_theory_completed = (
                existing.is_theory_completed or item.is_theory_completed
            )
            existing.is_quiz_passed = existing.is_quiz_passed or item.is_quiz_passed
            existing.score = max(existing.score, item.score)
            session.add(existing)

    # ---- Unlocked word sets ----
    for item in request.unlocked_word_sets:
        exists = session.exec(
            select(UserWordSetCrossRef).where(
                UserWordSetCrossRef.user_id == user_id,
                UserWordSetCrossRef.set_id == item.set_id,
            )
        ).first()
        if exists is None:
            session.add(
                UserWordSetCrossRef(user_id=user_id, set_id=item.set_id)
            )

    # ---- User profile ----
    if request.user_profile is not None:
        profile = request.user_profile
        current_user.coins = max(current_user.coins, profile.coins)
        current_user.current_streak = max(
            current_user.current_streak, profile.current_streak
        )
        current_user.longest_streak = max(
            current_user.longest_streak, profile.longest_streak
        )
        session.add(current_user)

    session.commit()

    return {"message": "Sync upload successful"}


# ---------------------------------------------------------------------------
# Download – Client pulls the latest data from the server
# ---------------------------------------------------------------------------


@router.get("/download", response_model=SyncDownloadResponse)
async def download_progress(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Return all learning progress for the authenticated user."""
    user_id = current_user.user_id

    # ---- Custom Words ----
    from model.dto.sync import WordSyncItem, WordSetSyncItem, WordSetCrossRefSyncItem

    words_records = session.exec(select(Word).where(Word.user_id == user_id)).all()
    words_list = [
        WordSyncItem(
            word_id=r.word_id,
            english_word=r.english_word,
            vietnamese_meaning=r.vietnamese_meaning,
            audio=r.audio,
        )
        for r in words_records
    ]

    # ---- Custom Word Sets ----
    word_sets_records = session.exec(select(WordSet).where(WordSet.user_id == user_id)).all()
    word_sets_list = [
        WordSetSyncItem(
            set_id=r.set_id,
            name=r.name,
            unlock_cost=r.unlock_cost,
        )
        for r in word_sets_records
    ]

    # ---- Word Set Cross Refs ----
    cross_refs = session.exec(select(WordSetCrossRef).where(WordSetCrossRef.user_id == user_id)).all()
    cross_refs_list = [
        WordSetCrossRefSyncItem(
            word_id=r.word_id,
            set_id=r.set_id,
        )
        for r in cross_refs
    ]

    # ---- Word SRS ----
    word_srs_records = session.exec(
        select(WordSrs).where(WordSrs.user_id == user_id)
    ).all()
    word_srs_list = [
        WordSrsDownload(
            word_id=r.word_id,
            level=r.level,
            next_review_date=r.next_review_date,
            last_review_date=r.last_review_date,
        )
        for r in word_srs_records
    ]

    # ---- Grammar progress ----
    grammar_records = session.exec(
        select(UserGrammarProgress).where(
            UserGrammarProgress.user_id == user_id
        )
    ).all()
    grammar_list = [
        GrammarProgressDownload(
            lesson_id=r.lesson_id,
            is_theory_completed=r.is_theory_completed,
            is_quiz_passed=r.is_quiz_passed,
            score=r.score,
        )
        for r in grammar_records
    ]

    # ---- Unlocked word sets ----
    unlocked_refs = session.exec(
        select(UserWordSetCrossRef).where(
            UserWordSetCrossRef.user_id == user_id
        )
    ).all()
    unlocked_ids = [ref.set_id for ref in unlocked_refs]

    # ---- User profile ----
    user_profile = UserProfileDownload(
        coins=current_user.coins,
        current_streak=current_user.current_streak,
        longest_streak=current_user.longest_streak,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
    )

    return SyncDownloadResponse(
        words_list=words_list,
        word_sets_list=word_sets_list,
        word_set_cross_refs_list=cross_refs_list,
        word_srs_list=word_srs_list,
        grammar_progress_list=grammar_list,
        unlocked_word_set_ids=unlocked_ids,
        user_profile=user_profile,
    )
