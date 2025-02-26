import copy
import json
import re
from pathlib import Path
from typing import List, TypeVar, Callable, Dict, Tuple, Iterator, Optional

from randovania.game_description import game_migration
from randovania.game_description.game_description import GameDescription, MinimalLogicData, IndexWithReason
from randovania.game_description.requirements import ResourceRequirement, \
    RequirementOr, RequirementAnd, Requirement, RequirementTemplate, RequirementArrayBase
from randovania.game_description.resources.item_resource_info import ItemResourceInfo
from randovania.game_description.resources.resource_database import ResourceDatabase
from randovania.game_description.resources.resource_info import ResourceInfo, ResourceGainTuple, ResourceGain
from randovania.game_description.resources.simple_resource_info import SimpleResourceInfo
from randovania.game_description.resources.trick_resource_info import TrickResourceInfo
from randovania.game_description.world.area import Area
from randovania.game_description.world.dock import DockWeaknessDatabase, DockWeakness
from randovania.game_description.world.node import Node, GenericNode, DockNode, PickupNode, TeleporterNode, EventNode, \
    ConfigurableNode, LogbookNode, LoreType, PlayerShipNode
from randovania.game_description.world.world import World
from randovania.game_description.world.world_list import WorldList


def write_resource_requirement(requirement: ResourceRequirement) -> dict:
    return {
        "type": "resource",
        "data": {
            "type": requirement.resource.resource_type.value,
            "name": requirement.resource.short_name,
            "amount": requirement.amount,
            "negate": requirement.negate,
        }
    }


def write_requirement_array(requirement: RequirementArrayBase, type_name: str) -> dict:
    return {
        "type": type_name,
        "data": {
            "comment": requirement.comment,
            "items": [
                write_requirement(item)
                for item in requirement.items
            ]
        }
    }


def write_requirement_template(requirement: RequirementTemplate) -> dict:
    return {
        "type": "template",
        "data": requirement.template_name
    }


def write_requirement(requirement: Requirement) -> dict:
    if isinstance(requirement, ResourceRequirement):
        return write_resource_requirement(requirement)

    elif isinstance(requirement, RequirementOr):
        return write_requirement_array(requirement, "or")

    elif isinstance(requirement, RequirementAnd):
        return write_requirement_array(requirement, "and")

    elif isinstance(requirement, RequirementTemplate):
        return write_requirement_template(requirement)

    else:
        raise ValueError(f"Unknown requirement type: {type(requirement)}")


# Resource

def write_resource_gain(resource_gain: ResourceGain) -> list:
    def sorter(item: Tuple[ResourceInfo, int]):
        return item[0].resource_type, item[0].short_name, item[1]

    return [
        {
            "resource_type": resource.resource_type.value,
            "resource_name": resource.short_name,
            "amount": gain,
        }
        for resource, gain in sorted(resource_gain, key=sorter)
    ]


def write_simple_resource(resource: SimpleResourceInfo) -> dict:
    return {
        "long_name": resource.long_name,
        "extra": unwrap_frozen(resource.extra),
    }


def write_item_resource(resource: ItemResourceInfo) -> dict:
    return {
        "long_name": resource.long_name,
        "max_capacity": resource.max_capacity,
        "extra": unwrap_frozen(resource.extra),
    }


def write_trick_resource(resource: TrickResourceInfo) -> dict:
    return {
        "long_name": resource.long_name,
        "description": resource.description,
        "extra": unwrap_frozen(resource.extra),
    }


X = TypeVar('X')


def write_array(array: List[X], writer: Callable[[X], dict]) -> dict:
    return {
        item.short_name: writer(item)
        for item in array
    }


def check_for_duplicated_index(array: List, field: str) -> Iterator[str]:
    indices_seen = set()
    for item in array:
        if getattr(item, field) in indices_seen:
            yield f"Duplicated index {getattr(item, field)} with {item.long_name}"
        else:
            indices_seen.add(getattr(item, field))


def write_resource_database(resource_database: ResourceDatabase):
    errors = []
    for array in (resource_database.item, resource_database.event, resource_database.trick, resource_database.damage,
                  resource_database.version, resource_database.misc):
        errors.extend(check_for_duplicated_index(array, "short_name"))

    if errors:
        raise ValueError("Errors in resource database: {}".format("\n".join(errors)))

    return {
        "items": write_array(resource_database.item, write_item_resource),
        "events": write_array(resource_database.event, write_simple_resource),
        "tricks": write_array(resource_database.trick, write_trick_resource),
        "damage": write_array(resource_database.damage, write_simple_resource),
        "versions": write_array(resource_database.version, write_simple_resource),
        "misc": write_array(resource_database.misc, write_simple_resource),
        "requirement_template": {
            name: write_requirement(requirement)
            for name, requirement in resource_database.requirement_template.items()
        },
        "damage_reductions": [
            {
                "name": resource.short_name,
                "reductions": [
                    {
                        "name": reduction.inventory_item.short_name if reduction.inventory_item is not None else None,
                        "multiplier": reduction.damage_multiplier
                    }
                    for reduction in reductions
                ]
            }
            for resource, reductions in resource_database.damage_reductions.items()
        ],
        "energy_tank_item_index": resource_database.energy_tank_item_index,
        "item_percentage_index": resource_database.item_percentage_index,
        "multiworld_magic_item_index": resource_database.multiworld_magic_item_index,
    }


# Dock Weakness Database

def write_dock_weakness(dock_weakness: DockWeakness) -> dict:
    return {
        "lock_type": dock_weakness.lock_type.value,
        "extra": dock_weakness.extra,
        "requirement": write_requirement(dock_weakness.requirement)
    }


def write_dock_weakness_database(database: DockWeaknessDatabase) -> dict:
    return {
        "types": {
            dock_type.short_name: {
                "name": dock_type.long_name,
                "extra": dock_type.extra,
                "items": {
                    name: write_dock_weakness(weakness)
                    for name, weakness in database.weaknesses[dock_type].items()
                }
            }
            for dock_type in database.dock_types
        },
        "default_weakness": {
            "type": database.default_weakness[0].short_name,
            "name": database.default_weakness[1].name,
        }
    }


# World/Area/Nodes

def unwrap_frozen(extra):
    if isinstance(extra, tuple):
        return [unwrap_frozen(value) for value in extra]

    elif isinstance(extra, dict):
        return {key: unwrap_frozen(value) for key, value in extra.items()}

    else:
        return extra


def write_node(node: Node) -> dict:
    """
    :param node:
    :return:
    """

    extra = unwrap_frozen(node.extra)
    data = {}
    common_fields = {
        "heal": node.heal,
        "coordinates": {"x": node.location.x, "y": node.location.y, "z": node.location.z} if node.location else None,
        "description": node.description,
        "extra": extra,
    }

    if isinstance(node, GenericNode):
        data["node_type"] = "generic"
        data.update(common_fields)

    elif isinstance(node, DockNode):
        data["node_type"] = "dock"
        data.update(common_fields)
        data["destination"] = node.default_connection.as_json
        data["dock_type"] = node.dock_type.short_name
        data["dock_weakness"] = node.default_dock_weakness.name

    elif isinstance(node, PickupNode):
        data["node_type"] = "pickup"
        data.update(common_fields)
        data["pickup_index"] = node.pickup_index.index
        data["major_location"] = node.major_location

    elif isinstance(node, TeleporterNode):
        data["node_type"] = "teleporter"
        data.update(common_fields)
        data["destination"] = node.default_connection.as_json
        data["keep_name_when_vanilla"] = node.keep_name_when_vanilla
        data["editable"] = node.editable

    elif isinstance(node, EventNode):
        data["node_type"] = "event"
        data.update(common_fields)
        data["event_name"] = node.resource().short_name

    elif isinstance(node, ConfigurableNode):
        data["node_type"] = "configurable_node"
        data.update(common_fields)

    elif isinstance(node, LogbookNode):
        data["node_type"] = "logbook"
        data.update(common_fields)
        data["string_asset_id"] = node.string_asset_id
        data["lore_type"] = node.lore_type.value

        if node.lore_type == LoreType.LUMINOTH_LORE:
            data["extra"]["translator"] = node.required_translator.short_name

        elif node.lore_type in {LoreType.LUMINOTH_WARRIOR, LoreType.SKY_TEMPLE_KEY_HINT}:
            data["extra"]["hint_index"] = node.hint_index

    elif isinstance(node, PlayerShipNode):
        data["node_type"] = "player_ship"
        data.update(common_fields)
        data["is_unlocked"] = write_requirement(node.is_unlocked)

    else:
        raise ValueError("Unknown node class: {}".format(node))

    return data


def write_area(area: Area) -> dict:
    """
    :param area:
    :return:
    """
    errors = []

    nodes = {}
    for node in area.nodes:
        try:
            data = write_node(node)
            data["connections"] = {
                target_node.name: write_requirement(area.connections[node][target_node])
                for target_node in area.nodes
                if target_node in area.connections[node]
            }
            nodes[node.name] = data
        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise ValueError("Area {} nodes has the following errors:\n* {}".format(
            area.name, "\n* ".join(errors)))

    extra = unwrap_frozen(area.extra)
    return {
        "default_node": area.default_node,
        "valid_starting_location": area.valid_starting_location,
        "extra": extra,
        "nodes": nodes,
    }


def write_world(world: World) -> dict:
    errors = []
    areas = {}
    for area in world.areas:
        try:
            areas[area.name] = write_area(area)
        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise ValueError("World {} has the following errors:\n> {}".format(
            world.name, "\n\n> ".join(errors)))

    extra = unwrap_frozen(world.extra)
    return {
        "name": world.name,
        "extra": extra,
        "areas": areas,
    }


def write_world_list(world_list: WorldList) -> list:
    errors = []
    known_indices = {}

    worlds = []
    for world in world_list.worlds:
        try:
            worlds.append(write_world(world))

            for node in world.all_nodes:
                if isinstance(node, PickupNode):
                    name = world_list.node_name(node, with_world=True, distinguish_dark_aether=True)
                    if node.pickup_index in known_indices:
                        errors.append(f"{name} has {node.pickup_index}, "
                                      f"but it was already used in {known_indices[node.pickup_index]}")
                    else:
                        known_indices[node.pickup_index] = name

        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise ValueError("\n\n".join(errors))

    return worlds


# Game Description

def write_initial_states(initial_states: Dict[str, ResourceGainTuple]) -> dict:
    return {
        name: write_resource_gain(initial_state)
        for name, initial_state in initial_states.items()
    }


def write_minimal_logic_db(db: Optional[MinimalLogicData]) -> Optional[dict]:
    if db is None:
        return None

    return {
        "items_to_exclude": [
            {"name": it.name, "when_shuffled": it.reason}
            for it in db.items_to_exclude
        ],
        "custom_item_amount": [
            {
                "name": index,
                "value": value
            }
            for index, value in db.custom_item_amount.items()
        ],
        "events_to_exclude": [
            {"name": it.name, "reason": it.reason}
            for it in db.events_to_exclude
        ]
    }


def write_game_description(game: GameDescription) -> dict:
    return {
        "schema_version": game_migration.CURRENT_VERSION,
        "game": game.game.value,
        "resource_database": write_resource_database(game.resource_database),

        "starting_location": game.starting_location.as_json,
        "initial_states": write_initial_states(game.initial_states),
        "minimal_logic": write_minimal_logic_db(game.minimal_logic),
        "victory_condition": write_requirement(game.victory_condition),

        "dock_weakness_database": write_dock_weakness_database(game.dock_weakness_database),
        "worlds": write_world_list(game.world_list),
    }


def write_as_split_files(data: dict, base_path: Path):
    data = copy.copy(data)
    worlds = data.pop("worlds")
    data["worlds"] = []

    for world in worlds:
        name = re.sub(r'[^a-zA-Z\- ]', r'', world["name"])
        data["worlds"].append(f"{name}.json")
        with base_path.joinpath(f"{name}.json").open("w", encoding="utf-8") as world_file:
            json.dump(world, world_file, indent=4)

    with base_path.joinpath(f"header.json").open("w", encoding="utf-8") as meta:
        json.dump(data, meta, indent=4)
