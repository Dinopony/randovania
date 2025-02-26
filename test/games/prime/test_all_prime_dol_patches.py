import dataclasses

import pytest

from randovania.dol_patching import assembler
from randovania.games.game import RandovaniaGame
from randovania.patching.prime import all_prime_dol_patches


@pytest.fixture(name="string_display")
def _string_display():
    return all_prime_dol_patches.StringDisplayPatchAddresses(
        update_hint_state=0x80038020,
        message_receiver_string_ref=0x9000,
        wstring_constructor=0x802ff3dc,
        display_hud_memo=0x8006b3c8,
        max_message_size=200,
    )


@pytest.fixture(name="powerup_address")
def _powerup_address():
    return all_prime_dol_patches.PowerupFunctionsAddresses(
        add_power_up=0x800758f0,
        incr_pickup=0x80075760,
        decr_pickup=0x800756c4,
    )


def test_apply_remote_execution_patch(dol_file, string_display: all_prime_dol_patches.StringDisplayPatchAddresses):
    dol_file.header = dataclasses.replace(
        dol_file.header,
        sections=tuple([dataclasses.replace(dol_file.header.sections[0],
                                            base_address=0x80038020),
                        *dol_file.header.sections[1:]]))

    # Run
    dol_file.set_editable(True)
    with dol_file:
        all_prime_dol_patches.apply_remote_execution_patch(string_display, dol_file)

    # Assert
    results = dol_file.dol_path.read_bytes()[0x100:]
    # for i in range(50):
    #     print("".join(f"\\x{x:02x}" for x in results[i * 20:(i + 1) * 20]))

    assert results == (b'\x94\x21\xff\xcc\x7c\x08\x02\xa6\x90\x01\x00\x38\xbf\xc1\x00\x2c\x7c\x7f\x1b\x78'
                       b'\x88\x9f\x00\x02\x2c\x04\x00\x00\x40\x82\x00\x18\xbb\xc1\x00\x2c\x80\x01\x00\x38'
                       b'\x7c\x08\x03\xa6\x38\x21\x00\x34\x4e\x80\x00\x20\x38\xc0\x00\x00\x98\xdf\x00\x02'
                       b'\x3f\xc0\x80\x03\x63\xde\x80\x7c\x38\x80\x01\x00\x7c\x04\xf7\xac\x2c\x04\x00\x00'
                       b'\x38\x84\xff\xe0\x40\x82\xff\xf4\x7c\x00\x04\xac\x4c\x00\x01\x2c\xbb\xc1\x00\x2c'
                       b'\x80\x01\x00\x38\x7c\x08\x03\xa6\x38\x21\x00\x34\x4e\x80\x00\x20\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       )


def test_create_remote_execution_body(string_display: all_prime_dol_patches.StringDisplayPatchAddresses,
                                      powerup_address: all_prime_dol_patches.PowerupFunctionsAddresses):
    # Run
    patch_address, patch_bytes = all_prime_dol_patches.create_remote_execution_body(string_display, [
        *all_prime_dol_patches.call_display_hud_patch(string_display),
        *all_prime_dol_patches.adjust_item_amount_and_capacity_patch(powerup_address, RandovaniaGame.METROID_PRIME_ECHOES, 3, 12),
    ])

    # Assert
    assert patch_address == string_display.update_hint_state + 0x60
    assert patch_bytes == (b'\x3c\xa0\x41\x00\x38\xc0\x00\x00\x38\xe0\x00\x01\x39\x20\x00\x09\x90\xa1\x00\x10'
                           b'\x98\xe1\x00\x14\x98\xc1\x00\x15\x98\xc1\x00\x16\x98\xe1\x00\x17\x91\x21\x00\x18'
                           b'\x38\x61\x00\x1c\x3c\x80\x00\x00\x60\x84\x90\x00\x48\x2c\x73\x29\x38\x81\x00\x10'
                           b'\x48\x03\x33\x0d\x80\x7f\x15\x0c\x38\x80\x00\x03\x38\xa0\x00\x0c\x48\x03\xd8\x25'
                           b'\x80\x7f\x15\x0c\x38\x80\x00\x03\x38\xa0\x00\x0c\x48\x03\xd6\x85\xbb\xc1\x00\x2c'
                           b'\x80\x01\x00\x38\x7c\x08\x03\xa6\x38\x21\x00\x34\x4e\x80\x00\x20')


def test_remote_execution_patch_start():
    # Run
    patch = all_prime_dol_patches.remote_execution_patch_start()
    data = bytes(assembler.assemble_instructions(0x80008020, patch))

    # Assert
    assert data == (b'\x94\x21\xff\xcc\x7c\x08\x02\xa6\x90\x01\x00\x38\xbf\xc1\x00\x2c\x7c\x7f\x1b\x78'
                    b'\x88\x9f\x00\x02\x2c\x04\x00\x00\x40\x82\x00\x18\xbb\xc1\x00\x2c\x80\x01\x00\x38'
                    b'\x7c\x08\x03\xa6\x38\x21\x00\x34\x4e\x80\x00\x20\x38\xc0\x00\x00\x98\xdf\x00\x02'
                    b'\x3f\xc0\x80\x00\x63\xde\x80\x7c\x38\x80\x01\x00\x7c\x04\xf7\xac\x2c\x04\x00\x00'
                    b'\x38\x84\xff\xe0\x40\x82\xff\xf4\x7c\x00\x04\xac\x4c\x00\x01\x2c')


def test_remote_execution_patch_end():
    # Run
    patch = all_prime_dol_patches.remote_execution_patch_end()
    data = bytes(assembler.assemble_instructions(1000, patch))

    # Assert
    assert data == b"\xbb\xc1\x00\x2c\x80\x01\x00\x38\x7c\x08\x03\xa6\x38\x21\x00\x34\x4e\x80\x00\x20"


def test_call_display_hud_patch(string_display: all_prime_dol_patches.StringDisplayPatchAddresses):
    # Run
    patch = all_prime_dol_patches.call_display_hud_patch(string_display)
    data = bytes(assembler.assemble_instructions(string_display.update_hint_state, patch))

    # Assert
    assert data == (b"\x3c\xa0\x41\x00\x38\xc0\x00\x00\x38\xe0\x00\x01\x39\x20\x00\x09\x90\xa1\x00\x10"
                    b"\x98\xe1\x00\x14\x98\xc1\x00\x15\x98\xc1\x00\x16\x98\xe1\x00\x17\x91\x21\x00\x18"
                    b"\x38\x61\x00\x1c\x3c\x80\x00\x00\x60\x84\x90\x00\x48\x2c\x73\x89\x38\x81\x00\x10"
                    b"\x48\x03\x33\x6d")


def test_give_item_patch(powerup_address: all_prime_dol_patches.PowerupFunctionsAddresses):
    # Run
    patch = all_prime_dol_patches.adjust_item_amount_and_capacity_patch(powerup_address, RandovaniaGame.METROID_PRIME_ECHOES, 10, 5)
    data = bytes(assembler.assemble_instructions(0x80008020, patch))

    # Assert
    assert data == (b"\x80\x7f\x15\x0c\x38\x80\x00\x0a\x38\xa0\x00\x05\x48\x06\xd8\xc5\x80\x7f\x15\x0c"
                    b"\x38\x80\x00\x0a\x38\xa0\x00\x05\x48\x06\xd7\x25")


def test_apply_reverse_energy_tank_heal_patch_active(dol_file):
    game = RandovaniaGame.METROID_PRIME_ECHOES
    addresses = all_prime_dol_patches.DangerousEnergyTankAddresses(
        small_number_float=0x1600,
        incr_pickup=0x2000,
    )

    # Run
    dol_file.set_editable(True)
    with dol_file:
        all_prime_dol_patches.apply_reverse_energy_tank_heal_patch(0x1500, addresses, False, game, dol_file)
        all_prime_dol_patches.apply_reverse_energy_tank_heal_patch(0x1500, addresses, True, game, dol_file)

    # Assert
    results = dol_file.dol_path.read_bytes()[0x100:]
    assert results == (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\xc0\x02\x01\x00\xd0\x1e\x00\x14\x60\x00\x00\x00\x60\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       )


def test_apply_reverse_energy_tank_heal_patch_inactive(dol_file):
    game = RandovaniaGame.METROID_PRIME_ECHOES
    addresses = all_prime_dol_patches.DangerousEnergyTankAddresses(
        small_number_float=0x1600,
        incr_pickup=0x2000,
    )

    # Run
    dol_file.set_editable(True)
    with dol_file:
        all_prime_dol_patches.apply_reverse_energy_tank_heal_patch(0x1500, addresses, True, game, dol_file)
        all_prime_dol_patches.apply_reverse_energy_tank_heal_patch(0x1500, addresses, False, game, dol_file)

    # Assert
    results = dol_file.dol_path.read_bytes()[0x100:]
    assert results == (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x7f\xc3\xf3\x78\x38\x80\x00\x29\x38\xa0\x27\x0f\x4b\xff\xff\x65'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       )
