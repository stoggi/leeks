from . import asset
from . import browser
from . import endpoint
from . import grafana
from . import impact
from . import operatingsystem
from . import person
from . import service

from . import common
from . import utils

import os
from ariadne import load_schema_from_path

schema_path = os.path.dirname(os.path.realpath(__file__))
type_defs = load_schema_from_path(schema_path)

resolvers = [
    *asset.resolvers,
    *browser.resolvers,
    *endpoint.resolvers,
    *grafana.resolvers,
    *impact.resolvers,
    *operatingsystem.resolvers,
    *person.resolvers,
    *service.resolvers,

    *common.resolvers,
]