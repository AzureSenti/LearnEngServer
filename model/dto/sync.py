from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Upload: Client → Server
# ---------------------------------------------------------------------------


class WordSrsUpload(BaseModel):
    """Single word SRS record sent from the client."""

    word_id: int
    level: int
    next_review_date: int
    last_review_date: int | None = None


class GrammarProgressUpload(BaseModel):
    """Single grammar progress record sent from the client."""

    lesson_id: int
    is_theory_completed: bool
    is_quiz_passed: bool
    score: int


class UserWordSetUpload(BaseModel):
    """Unlocked word set record sent from the client."""

    set_id: int


class UserProfileUpload(BaseModel):
    """User profile fields that can be synced."""

    coins: int
    current_streak: int
    longest_streak: int


class WordSyncItem(BaseModel):
    """Custom word record sent/received from client."""
    word_id: int
    english_word: str
    vietnamese_meaning: str
    audio: str | None = None

class WordSetSyncItem(BaseModel):
    """Custom word set record sent/received from client."""
    set_id: int
    name: str
    unlock_cost: int

class WordSetCrossRefSyncItem(BaseModel):
    """Word to WordSet link sent/received from client."""
    word_id: int
    set_id: int


class SyncUploadRequest(BaseModel):
    """Full upload payload from the client."""

    words_list: list[WordSyncItem] = []
    word_sets_list: list[WordSetSyncItem] = []
    word_set_cross_refs_list: list[WordSetCrossRefSyncItem] = []

    word_srs_list: list[WordSrsUpload] = []
    grammar_progress_list: list[GrammarProgressUpload] = []
    unlocked_word_sets: list[UserWordSetUpload] = []
    user_profile: UserProfileUpload | None = None


# ---------------------------------------------------------------------------
# Download: Server → Client
# ---------------------------------------------------------------------------


class WordSrsDownload(BaseModel):
    """Single word SRS record returned to the client."""

    word_id: int
    level: int
    next_review_date: int
    last_review_date: int | None = None


class GrammarProgressDownload(BaseModel):
    """Single grammar progress record returned to the client."""

    lesson_id: int
    is_theory_completed: bool
    is_quiz_passed: bool
    score: int


class UserProfileDownload(BaseModel):
    """User profile returned to the client."""

    coins: int
    current_streak: int
    longest_streak: int
    full_name: str
    avatar_url: str


class SyncDownloadResponse(BaseModel):
    """Full download payload sent to the client."""

    words_list: list[WordSyncItem] = []
    word_sets_list: list[WordSetSyncItem] = []
    word_set_cross_refs_list: list[WordSetCrossRefSyncItem] = []

    word_srs_list: list[WordSrsDownload] = []
    grammar_progress_list: list[GrammarProgressDownload] = []
    unlocked_word_set_ids: list[int] = []
    user_profile: UserProfileDownload
