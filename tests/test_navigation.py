from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "music_bot_user_mixes.py").read_text(encoding="utf-8")


def test_private_menu_navigation_is_before_transient_state_handling():
    start = SOURCE.index('async def handle_message(')
    end = SOURCE.index('async def ', start + 10)
    section = SOURCE[start:end]
    private_start = section.index('    if chat_type == "private":')
    private_section = section[private_start:]
    menu_marker = 'menu_action = _private_menu_action(message_text)'
    state_marker = '        state = await bot_instance.get_user_state(user_id)'
    assert menu_marker in private_section
    assert state_marker in private_section
    assert private_section.index(menu_marker) < private_section.index(state_marker)


def test_all_problematic_private_menu_labels_are_reserved():
    for label in (
        '"❤️ Избранное": "favorites"',
        '"📚 История": "history"',
        '"🔥 Чарты": "charts"',
        '"🎧 Похожие": "similar"',
        '"⚙️ Настройки": "settings"',
        '"❓ Помощь": "help"',
    ):
        assert label in SOURCE
