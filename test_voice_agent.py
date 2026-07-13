"""Runnable checks. `python test_voice_agent.py` — no framework needed."""
import questions


def test_pick_two_distinct():
    for _ in range(200):
        a, b = questions.pick_two()
        assert a["id"] != b["id"], "picked the same question twice"
        assert a in questions.QUESTIONS and b in questions.QUESTIONS


def test_pick_two_covers_all_six():
    seen = set()
    for _ in range(500):
        for q in questions.pick_two():
            seen.add(q["id"])
    assert seen == {0, 1, 2, 3, 4, 5}, f"not all questions reachable: {seen}"


def test_text_for():
    assert questions.text_for(0).startswith("How would you rate your sleep")
    assert questions.text_for(99) is None


if __name__ == "__main__":
    test_pick_two_distinct()
    test_pick_two_covers_all_six()
    test_text_for()
    print("ok")
