from __future__ import annotations

import contextlib
import random
from collections.abc import AsyncIterator
from pathlib import Path

from chia_rs import ConsensusConstants

from chia.consensus.block_height_map import BlockHeightMap
from chia.consensus.blockchain import Blockchain
from chia.full_node.block_store import BlockStore
from chia.full_node.coin_store import CoinStore
from chia.util.db_wrapper import DBWrapper2


@contextlib.asynccontextmanager
async def create_ram_blockchain(
    consensus_constants: ConsensusConstants,
) -> AsyncIterator[tuple[DBWrapper2, Blockchain]]:
    uri = f"file:db_{random.randint(0, 99999999)}?mode=memory&cache=shared"
    async with DBWrapper2.managed(database=uri, uri=True, reader_count=1, db_version=2) as db_wrapper:
        block_store = await BlockStore.create(db_wrapper)
        coin_store = await CoinStore.create(db_wrapper)
        height_map = await BlockHeightMap.create(Path("."), db_wrapper)
        blockchain = await Blockchain.create(coin_store, block_store, height_map, consensus_constants, 2)
        try:
            yield db_wrapper, blockchain
        finally:
            blockchain.shut_down()
