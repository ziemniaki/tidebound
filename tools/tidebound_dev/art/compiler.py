"""Export approved custom assets into Essentials' filename conventions."""

from . import ownership, props


def build(root):
    owners, exports = ownership.inventory(root)
    records = props.load(root)
    ownership.remove_retired(root, owners)
    for export in exports:
        export.write(root)
    props.write(root, records)
    ownership.publish(root, owners)
