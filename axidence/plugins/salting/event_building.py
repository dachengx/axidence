import strax
from strax import Plugin


class SaltingEvents(Plugin):
    __version__ = "0.0.0"
    depends_on = ("salting_peaks", "salting_peak_proximity", "peak_basics")
    provides = "events"
    data_kind = "events"
    save_when = strax.SaveWhen.EXPLICIT

    dtype = strax.time_fields


class SaltingEventBasics(Plugin):
    __version__ = "0.0.0"
    depends_on = ("events", "salting_peaks", "peak_basics", "peak_positions")
    provides = "event_basics"
    data_kind = "events"
    save_when = strax.SaveWhen.EXPLICIT

    dtype = strax.time_fields
