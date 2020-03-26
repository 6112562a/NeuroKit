# -*- coding: utf-8 -*-
import pandas as pd


from .emg_eventrelated import emg_eventrelated
from .emg_intervalrelated import emg_intervalrelated


def emg_analyze(data, sampling_rate=1000, method="auto"):
    """Performs EMG analysis on either epochs (event-related
    analysis) or on longer periods of data such as resting-state data.

    Parameters
    ----------
    data : dict, DataFrame
        A dictionary of epochs, containing one DataFrame per epoch,
        usually obtained via `epochs_create()`, or a DataFrame
        containing all epochs, usually obtained via `epochs_to_df()`.
        Can also take a DataFrame of processed signals from
        a longer period of data, typically generated by `emg_process()`
        or `bio_process()`. Can also take a dict containing sets of
        separate periods of data.
    sampling_rate : int
        The sampling frequency of the signal (in Hz, i.e., samples/second).
        Defaults to 1000Hz.
    method : str
        Can be one of 'event-related' for event-related analysis on epochs,
        or 'interval-related' for analysis on longer periods of data. Defaults
        to 'auto' where the right method will be chosen based on the
        mean duration of the data ('event-related' for duration under 10s).

    Returns
    -------
    DataFrame
        A dataframe containing the analyzed EMG features. If
        event-related analysis is conducted, each epoch is indicated
        by the `Label` column. See `emg_eventrelated()` and
        `emg_intervalrelated()` docstrings for details.

    See Also
    --------
    bio_process, emg_process, epochs_create, emg_eventrelated, emg_intervalrelated

    Examples
    ----------
    >>> import neurokit2 as nk
    >>> import pandas as pd

    >>> # Example with simulated data
    >>> emg = nk.emg_simulate(duration=20, sampling_rate=1000, n_bursts=3)
    >>> emg_signals, info = nk.emg_process(emg, sampling_rate=1000)
    >>> epochs = nk.epochs_create(emg_signals, events=[3000, 6000, 9000],
                                  sampling_rate=1000,
                                  epochs_start=-0.1, epochs_end=1.9)
    >>>
    >>> # Event-related analysis
    >>> nk.emg_analyze(epochs, method="event-related")
    >>>
    >>> # Interval-related analysis
    >>> nk.emg_analyze(emg_signals, method="interval-related")
    """
    method = method.lower()

    # Event-related analysis
    if method in ["event-related", "event", "epoch"]:
        # Sanity checks
        if isinstance(data, dict):
            for i in data:
                colnames = data[i].columns.values
        elif isinstance(data, pd.DataFrame):
            colnames = data.columns.values

        if len([i for i in colnames if "Label" in i]) == 0:
            raise ValueError("NeuroKit error: emg_analyze(): Wrong input"
                             "or method, we couldn't extract"
                             "extract epochs features.")
        else:
            features = emg_eventrelated(data)

    # Interval-related analysis
    elif method in ["interval-related", "interval", "resting-state"]:
        features = emg_intervalrelated(data)

    # Auto
    elif method in ["auto"]:

        if isinstance(data, dict):
            for i in data:
                duration = len(data[i]) / sampling_rate
            if duration >= 10:
                features = emg_intervalrelated(data)
            else:
                features = emg_eventrelated(data)

        if isinstance(data, pd.DataFrame):
            duration = len(data) / sampling_rate
            if duration >= 10:
                features = emg_intervalrelated(data)
            else:
                features = emg_eventrelated(data)

    return features
