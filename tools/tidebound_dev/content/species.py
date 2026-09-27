"""One definition catalog for PBS and native data.

Forms inherit their ordinary species; new species state a template for unchanged
engine attributes. Forward evolution rules generate family backlinks.
"""

from . import plants, insects, coastal


def combine(attribute):
    catalog = {}
    for family in (plants, insects, coastal):
        records = getattr(family, attribute)
        duplicates = catalog.keys() & records.keys()
        if duplicates:
            raise ValueError(
                f"Duplicate {attribute} IDs in {family.__name__}: {sorted(duplicates)}"
            )
        catalog.update(records)
    return catalog


SPECIES = combine("SPECIES")
METRICS = combine("METRICS")
CRIES = combine("CRIES")
