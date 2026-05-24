import json
from pathlib import Path

def is_hex(val: str) -> bool:
    return val.startswith("0x") or any(c in val.upper() for c in "ABCDEF")


def write_json_file(file_name, folder, data):
    file_path = Path("output") / folder
    file_path.mkdir(parents=True, exist_ok=True)

    full_path = file_path / f"{file_name}.json"

    with open(full_path, "w", encoding="utf-8") as file_object:
        json.dump(data, file_object, indent=2)


def create_clothing_entry(clothing_base, setup_did, gfx_object, texture_pairs: list):
    """
    texture_pairs should be a list like:
    [
        ("0x0500243D", "0x0500234A"),
        ("0x0500243E", "0x0500234B")
    ]
    """

    clo_texture_effects = []

    for old_texture, new_texture in texture_pairs:
        clo_texture_effects.append({
            "oldTexture": old_texture,
            "newTexture": new_texture
        })

    data = {
        "id": clothing_base,
        "clothingBaseEffects": {
            setup_did: {
                "cloObjectEffects": [
                    {
                        "index": 0,
                        "modelId": gfx_object,
                        "cloTextureEffects": clo_texture_effects
                    }
                ]
            }
        }
    }

    return data

