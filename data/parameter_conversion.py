# %% Imports
import pandas as pd

# %% Read in and definitions
df_param_old = pd.read_csv("parameters_old.csv")
seconds_per_day = 24 * 3600
mm_per_m = 1000
area_catchment_m2 = 115_000_000  # m^2 (approximate area of the catchment)

# %% Change units
df_param_new = df_param_old.copy()
units_old = ["m^3", "m^3/s", "s^-1"]
units_new = ["mm", "mm/d", "d^-1"]
numerical_columns = ["Minimum", "Maximum", "Value"]
for unit_old, unit_new in zip(units_old, units_new):
    if unit_old == "m^3":
        conversion_factor = mm_per_m / area_catchment_m2
    elif unit_old == "m^3/s":
        conversion_factor = mm_per_m * seconds_per_day / area_catchment_m2
    elif unit_old == "s^-1":
        conversion_factor = seconds_per_day
    else:
        raise ValueError(f"Unknown unit: {unit_old}")
    df_param_new.loc[df_param_new["Units"] == unit_old, numerical_columns] *= (
        conversion_factor
    )
    df_param_new.loc[df_param_new["Units"] == unit_old, "Units"] = unit_new

# %% Change alpha parameter values
min_alpha, max_alpha, default_alpha = 0.5, 1.0, 0.8
df_param_new.loc[df_param_new["Parameter"] == "alpha", numerical_columns] = [
    min_alpha,
    max_alpha,
    default_alpha,
]


# %%  Round the numerical values to 2 significant digits
df_param_new[numerical_columns] = df_param_new[numerical_columns].apply(
    lambda col: col.apply(lambda x: float(f"{x:.2g}"))
)
df_param_new.to_csv("parameters_new.csv", index=False)
