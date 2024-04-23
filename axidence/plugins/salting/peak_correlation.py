import numba
import numpy as np
import strax
from strax import Plugin
from straxen import PeakProximity

from axidence.plugin import InferDtypePlugin


class SaltingPeakProximity(PeakProximity, InferDtypePlugin):
    __version__ = "0.0.0"
    depends_on = ("salting_peaks", "peak_basics")
    provides = "salting_peak_proximity"
    data_kind = "salting_peaks"
    save_when = strax.SaveWhen.EXPLICIT

    def refer_dtype(self):
        return strax.merged_dtype([strax.to_numpy_dtype(super(SaltingPeakProximity, self).dtype)])

    def infer_dtype(self):
        dtype_reference = self.refer_dtype()
        required_names = ["time", "endtime", "n_competing", "n_competing_left"]
        dtype = self.copy_dtype(dtype_reference, required_names)
        # since event_number is int64 in event_basics
        dtype += [
            (("Salting number of peaks", "salt_number"), np.int64),
        ]
        return dtype

    def compute(self, salting_peaks, peaks):
        windows = strax.touching_windows(peaks, salting_peaks, window=self.nearby_window)
        n_left, n_tot = self.find_n_competing(
            peaks, salting_peaks, windows, fraction=self.min_area_fraction
        )
        return dict(
            time=salting_peaks["time"],
            endtime=strax.endtime(salting_peaks),
            n_competing=n_tot,
            n_competing_left=n_left,
            salt_number=salting_peaks["salt_number"],
        )

    @staticmethod
    @numba.jit(nopython=True, nogil=True, cache=True)
    def find_n_competing(peaks, salting_peaks, windows, fraction):
        n_left = np.zeros(len(salting_peaks), dtype=np.int32)
        n_tot = n_left.copy()
        areas = peaks["area"]
        salting_areas = salting_peaks["area"]

        dig = np.searchsorted(peaks["center_time"], salting_peaks["center_time"])

        for i, peak in enumerate(salting_peaks):
            left_i, right_i = windows[i]
            threshold = salting_areas[i] * fraction
            n_left[i] = np.sum(areas[left_i : dig[i]] > threshold)
            n_tot[i] = n_left[i] + np.sum(areas[dig[i] : right_i] > threshold)

        return n_left, n_tot


class SaltingPeakShadow(Plugin):
    __version__ = "0.0.0"
    depends_on = ("salting_peaks", "peak_basics", "peak_positions")
    provides = "peak_shadow"
    data_kind = "salting_peaks"
    save_when = strax.SaveWhen.EXPLICIT

    dtype = strax.time_fields


class SaltingPeakAmbience(Plugin):
    __version__ = "0.0.0"
    depends_on = ("salting_peaks", "peak_basics", "peak_positions")
    provides = "peak_ambience"
    data_kind = "salting_peaks"
    save_when = strax.SaveWhen.EXPLICIT

    dtype = strax.time_fields


class SaltingPeakSEDensity(Plugin):
    __version__ = "0.0.0"
    depends_on = ("salting_peaks", "peak_basics", "peak_positions")
    provides = "salting_peak_se_density"
    data_kind = "salting_peaks"
    save_when = strax.SaveWhen.EXPLICIT

    dtype = strax.time_fields
