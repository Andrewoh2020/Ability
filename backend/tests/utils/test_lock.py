from uuid import uuid4
import pytest
from app.utils.lock import LockPrefix, make_lock_id


uuid = uuid4()


@pytest.mark.parametrize(
    "prefix, id, expected",
    [
        (
            LockPrefix.REBUILD_APP,
            int(f"{uuid.int}"[:9]),
            int(f"{LockPrefix.REBUILD_APP.value}{int(f'{uuid.int}'[:9])}"),
        ),
    ],
)
def test_make_lock_id(prefix, id, expected):
    actual = make_lock_id(prefix, id)
    assert actual == expected
    s = f"{actual}"
    assert int(s[:2]) == prefix.value
    assert int(s[2:]) == id
