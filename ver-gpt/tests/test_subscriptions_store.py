from pathlib import Path

from arxiv_cli.storage.subscriptions import Subscription, SubscriptionsState, SubscriptionsStore


def test_subscriptions_store_add_list_remove(tmp_path: Path):
    store = SubscriptionsStore(tmp_path / "subs.json")

    s = Subscription.create(query="LLM agents", categories=["cs.AI"])
    store.add(s)

    subs = store.load()
    assert len(subs) == 1
    assert subs[0].id == s.id

    assert store.remove(s.id) is True
    assert store.load() == []
    assert store.remove("missing") is False


def test_subscriptions_state_seen_ids(tmp_path: Path):
    state = SubscriptionsState(tmp_path / "state.json")

    assert state.get_seen("x") == set()
    state.set_seen("x", {"a", "b"})
    assert state.get_seen("x") == {"a", "b"}
    state.remove("x")
    assert state.get_seen("x") == set()
