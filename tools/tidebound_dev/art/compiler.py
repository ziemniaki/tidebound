"""Export approved custom assets into Essentials' filename conventions."""

from . import ownership, props
from ..catalog import validate_names


def build(root):
    validate_names(root)
    owners, exports = ownership.inventory(root)
    records = props.load(root)
    ownership.publish(root, owners)
    for export in exports:
        export.write(root)
    props.write(root, records)
