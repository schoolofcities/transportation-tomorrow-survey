import pandas as pd
import geopandas as gpd
import os


dfq1 = pd.read_csv('metrics_tts2022.csv')

gdf = gpd.read_file('tts2022zones.geojson')

gdf = gdf.merge(dfq1, how='left', left_on='TTS2022', right_on='tts22_hhld')

gdf = gdf.to_crs("EPSG:32617")



# compute metrics for the maps

# area
gdf["area_km2"] = gdf.geometry.area / 1_000_000

# population density (5 and up)
gdf["population"] = gdf["persons_htable"]
gdf["population_density"] = gdf["population"] / gdf["area_km2"]

# low income - % make less than $60k
gdf["low_income_hhlds_percent"] = 100 * (gdf["hhld_income_group_1"] + gdf["hhld_income_group_2"] + gdf["hhld_income_group_3"]) / (gdf["hhld_income_group_1"] + gdf["hhld_income_group_2"] + gdf["hhld_income_group_3"] + gdf["hhld_income_group_4"] + gdf["hhld_income_group_5"] + gdf["hhld_income_group_6"] + gdf["hhld_income_group_7"] + gdf["hhld_income_group_8"] + gdf["hhld_income_group_9"])

# immigrated in past 2 years / non citizen
gdf["immig_recent"] = 100 * (gdf["immig_2year"] + gdf["immig_nonpr"]) / (gdf["immig_2year"] + gdf["immig_nonpr"] + gdf["immig_2to5year"] + gdf["immig_5to10year"] + gdf["immig_10to15year"] + gdf["immig_15moreyear"] + gdf["immig_no"])

# bike
gdf["mode_bike"] = 100 * gdf["trip_mode_prime_C"] / gdf["trips_total"]

# walk
gdf["mode_walk"] = 100 * gdf["trip_mode_prime_W"] / gdf["trips_total"]

# transit
gdf["mode_transit"] = 100 * (gdf["trip_mode_prime_B"] + gdf["trip_mode_prime_G"] + gdf["trip_mode_prime_J"]) / gdf["trips_total"]

# car
gdf["mode_drive"] = 100 * (gdf["trip_mode_prime_D"] + gdf["trip_mode_prime_P"] + gdf["trip_mode_prime_T"] + gdf["trip_mode_prime_U"]) / gdf["trips_total"]

# trips less that 5km %
gdf["trips_less5km_percent"] = 100 * gdf["trips_less5km"] / gdf["trips_total"]

# trips less that 5km that are by car %
gdf["trips_less5km_percent_car"] = 100 * gdf["trips_less5km_car"] / gdf["trips_less5km"]

# children driven to school
gdf["children_driven_to_school"] = 100 * gdf["trip_home_school_car"] / gdf["trip_home_school_total"]

# drivers licence %
gdf["drivers_lic_perperson_20to75"] = 100 * gdf["drivers_lic_perperson_20to75"]



# final metrics to save
gdf = gdf[[
	"TTS2022",
	"population",
	"hhlds",
	"hhld_sample",
	"population_density", 
	"low_income_hhlds_percent",
	"immig_recent",
	"veh_per_hhld",
	"drivers_lic_perperson_20to75",
	"transpass_perperson_6up",
	"trip_km_avg",
	"trips_5up_per_person",
	"activities_mean",
	"mode_bike",
	"mode_walk",
	"mode_transit",
	"mode_drive",
	"trips_less5km_percent",
	"trips_less5km_percent_car",
	"children_driven_to_school",
	"geometry"
]]

# save to new file
gdf = gdf.to_crs("EPSG:4326")
gdf.to_file("tts2022zones_data.geojson", driver="GeoJSON")

# convert geojson to PMTiles
os.system("rm tts2022zones_data.pmtiles")
os.system("tippecanoe -zg -o tts2022zones_data.pmtiles --no-feature-limit --extend-zooms-if-still-dropping tts2022zones_data.geojson")

