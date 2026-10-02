from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "music_bot_user_mixes.py").read_text(encoding="utf-8")
CONFIG = (ROOT / "config.py").read_text(encoding="utf-8")


def test_search_ui_has_no_favorite_button_in_results():
    assert 'InlineKeyboardButton("♡", callback_data=f"favtoggle:{session_id}:{uid}")' not in SOURCE
    assert 'InlineKeyboardButton("❤️", callback_data=f"favtoggle:{session_id}:{uid}")' not in SOURCE
    assert 'После скачивания появится кнопка «Добавить в избранное».' in SOURCE
    assert 'InlineKeyboardButton("👥 Похожие", callback_data=f"similar_search:{session_id}")' in SOURCE
    assert 'InlineKeyboardButton("✕ Закрыть", callback_data="close_search")' in SOURCE


def test_downloaded_audio_has_native_favorite_callback():
    assert 'InlineKeyboardButton("❤️ Добавить в избранное", callback_data=callback_data)' in SOURCE
    assert 'callback_data = f"fav_audio:{uid}"' in SOURCE
    assert "elif callback_data.startswith('fav_audio:')" in SOURCE
    assert "elif callback_data.startswith('fav_audio_remove:')" in SOURCE


def test_search_page_defaults_to_eight_tracks():
    assert "SONGS_PER_PAGE = 8" in CONFIG
