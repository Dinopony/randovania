from randovania.games.game import GameData, GameGenerator, GameGui, GameLayout, GamePresetDescriber
from randovania.games.prime3.generator.item_pool.pool_creator import corruption_specific_pool
from randovania.games.prime3.layout.corruption_configuration import CorruptionConfiguration
from randovania.games.prime3.layout.corruption_cosmetic_patches import CorruptionCosmeticPatches
from randovania.games.prime3.layout.preset_describer import corruption_format_params, corruption_unexpected_items, corruption_expected_items


def _corruption_gui():
    from randovania.games.prime3.gui.preset_settings import prime3_preset_tabs
    from randovania.games.prime3.gui.dialog.corruption_cosmetic_patches_dialog import CorruptionCosmeticPatchesDialog

    return GameGui(
        tab_provider=prime3_preset_tabs,
        cosmetic_dialog=CorruptionCosmeticPatchesDialog,
    )


game_data: GameData = GameData(
    short_name="Corruption",
    long_name="Metroid Prime 3: Corruption",
    experimental=True,

    presets=[
        {
            "path": "starter_preset.rdvpreset"
        }
    ],

    layout=GameLayout(
        configuration=CorruptionConfiguration,
        cosmetic_patches=CorruptionCosmeticPatches,
        preset_describer=GamePresetDescriber(
            expected_items=corruption_expected_items,
            unexpected_items=corruption_unexpected_items,
            format_params=corruption_format_params
        )
    ),

    gui=_corruption_gui,

    generator=GameGenerator(
        item_pool_creator=corruption_specific_pool
    )
)
