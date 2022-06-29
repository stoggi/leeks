from ariadne import InterfaceType, ObjectType, UnionType

interface_node = InterfaceType("Node")
operating_system = ObjectType("OperatingSystem")
browser = ObjectType("Browser")

@browser.field("version")
@operating_system.field("version")
def resolve_version(obj, info):
    major = obj.get("major", 0)
    minor = obj.get("minor", 0)
    patch = obj.get("patch", 0)
    build = obj.get("build", '')
    return "{}.{}.{}.{}".format(major, minor, patch, build)


@interface_node.type_resolver
def resolve_interface_node(obj, *_):
    if obj["label"] in [
        "Asset",
        "Browser",
        "Endpoint",
        "Impact",
        "OperatingSystem",
        "Person",
        "Service",
    ]:
        return obj["label"]
    else:
        return None

def resolve_error_type(obj, *_):
    if "message" in obj.keys():
        return "Error"
    else:
        return obj["label"]

resolvers = [
    operating_system,
    interface_node,
    browser,
    UnionType("AssetResult", resolve_error_type),
    UnionType("BrowserResult", resolve_error_type),
    UnionType("EndpointResult", resolve_error_type),
    UnionType("ImpactResult", resolve_error_type),
    UnionType("OperatingSystemResult", resolve_error_type),
    UnionType("PersonResult", resolve_error_type),
    UnionType("ServiceResult", resolve_error_type),
]
