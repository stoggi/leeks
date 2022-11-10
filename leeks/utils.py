

def agtype_to_dict(obj):
    return {
        "id": obj.id,
        "label": obj.label,
        **obj.properties,
    }

def node_to_dict(obj):
    return {
        "id": obj.id,
        "label": ",".join(obj.labels),
        **obj,
    }

def edge_to_dict(obj):
    return {
        "id": obj.id,
        "label": obj.type,
        **obj,
    }