from randovania.games.prime2.layout.echoes_configuration import EchoesConfiguration
from randovania.games.prime2.generator.item_pool.dark_temple_keys import add_dark_temple_keys
from randovania.games.prime2.generator.item_pool.sky_temple_keys import add_sky_temple_key_distribution_logic
from randovania.generator.item_pool.pool_creator import _extend_pool_results
from randovania.generator.item_pool import PoolResults
from randovania.game_description.resources.resource_database import ResourceDatabase


def echoes_specific_pool(results: PoolResults, configuration: EchoesConfiguration, db: ResourceDatabase):
    # Adding Dark Temple Keys to pool
    _extend_pool_results(results, add_dark_temple_keys(db))

    # Adding Sky Temple Keys to pool
    _extend_pool_results(results, add_sky_temple_key_distribution_logic(db, configuration.sky_temple_keys))
