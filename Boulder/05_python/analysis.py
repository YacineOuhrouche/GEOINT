def feature_count(layer):
    if layer is None:
        return 0

    return len(layer)

def calculate_statistics(layers):
    stats = {}

    stats["Buildings"] = feature_count(layers.get("Buildings"))
    stats["Transit Stops"] = feature_count(layers.get("Transit Stops"))
    stats["Schools"] = feature_count(layers.get("Schools"))
    stats["Fire Stations"] = feature_count(layers.get("Fire Stations"))
    stats["Bridges"] = feature_count(layers.get("Bridges"))

    return stats