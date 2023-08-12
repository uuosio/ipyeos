import time
from ipyeos import log
from ipyeos.multi_index import key_u64_value_double_index, secondary_double_index

logger = log.get_logger(__name__)

def test_key_u64_value_double_index():
    idx = key_u64_value_double_index()

    idx.create(1, 1.1)
    idx.create(2, 1.3)
    idx.create(3, 1.2)
    assert (1, 1.1) == idx.pop_first()
    assert (2, 1.3) == idx.pop_first()
    assert (3, 1.2) == idx.pop_first()

    idx.create(1, 1.1)
    idx.create(2, 1.3)
    idx.create(3, 1.2)

    ret = idx.find(1)
    assert ret == 1.1

    ret = idx.lower_bound(1, 1.1)
    assert ret == (1, 1.1), "lower_bound failed"

    ret = idx.upper_bound(1, 1.1)
    logger.info(ret)
    assert ret == (2, 1.3), "upper_bound failed"

    ret = idx.modify(1, 1.2)
    assert ret

    ret = idx.find(1)
    assert ret == 1.2

    ret = idx.lower_bound(1, 1.1)
    assert ret == (1, 1.2), "lower_bound failed"

    ret = idx.upper_bound(1, 1.1)
    logger.info(ret)
    assert ret == (1, 1.2), "upper_bound failed"

    ret = idx.upper_bound(1, 1.2)
    logger.info(ret)
    assert ret == (2, 1.3), "upper_bound failed"

    ret = idx.first()
    assert ret, "first failed"
    first, second = ret
    assert second == 1.2 and first == 1, "first failed"

    start = time.monotonic()
    for i in range(4, 100000):
        idx.create(i, 1.1)
    duration = time.monotonic() - start
    logger.info("create 0 items: %f", duration)
    logger.info(idx.row_count())

    start = time.monotonic()
    while idx.pop_first():
        pass
    logger.info("pop 100000 items: %f", time.monotonic() - start)


def test_secondary_double_index():
    idx = secondary_double_index()

    idx.create(1, 1.1)
    idx.create(3, 1.2)
    idx.create(2, 1.3)
    assert (1, 1.1) == idx.pop_first()
    assert (3, 1.2) == idx.pop_first()
    assert (2, 1.3) == idx.pop_first()

    idx.create(1, 1.1)
    idx.create(3, 1.2)
    idx.create(2, 1.3)

    ret = idx.find_by_second(1.1)
    assert ret == 1

    ret = idx.lower_bound(1, 1.1)
    assert ret == (1, 1.1), "lower_bound failed"

    ret = idx.upper_bound(1, 1.1)
    logger.info(ret)
    assert ret == (3, 1.2), "upper_bound failed"

    ret = idx.modify(1, 1.2)
    assert ret

    ret = idx.find_by_second(1.2)
    assert ret == 1

    ret = idx.lower_bound(1, 1.1)
    assert ret == (1, 1.2), "lower_bound failed"

    ret = idx.upper_bound(1, 1.1)
    logger.info(ret)
    assert ret == (1, 1.2), "upper_bound failed"

    ret = idx.upper_bound(1, 1.2)
    logger.info(ret)
    assert ret == (3, 1.2), "upper_bound failed"

    ret = idx.first()
    assert ret, "first failed"
    first, second = ret
    assert second == 1.2 and first == 1, "first failed"

    start = time.monotonic()
    for i in range(4, 100000):
        idx.create(i, 1.1)
    duration = time.monotonic() - start
    logger.info("create 0 items: %f", duration)
    logger.info(idx.row_count())

    start = time.monotonic()
    while idx.pop_first():
        pass
    logger.info("pop 100000 items: %f", time.monotonic() - start)
