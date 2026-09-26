"""One definition catalog for PBS and native data.

Forms inherit their ordinary species; new species state a template for unchanged
engine attributes. Forward evolution rules generate family backlinks.
"""
from . import plants, insects, coastal

SPECIES = plants.SPECIES | insects.SPECIES | coastal.SPECIES
METRICS = plants.METRICS | insects.METRICS | coastal.METRICS
CRIES = plants.CRIES | insects.CRIES | coastal.CRIES
