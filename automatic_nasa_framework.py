"""NASA metadata and prototype habitat-scoring framework.

This module is educational software. Generated environmental grids and
heuristic scores are not satellite measurements or validated ecology.
"""

import requests
import json
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import sys


def _configure_console_output():
    """Avoid Unicode logging failures on Windows consoles using legacy encodings."""
    if sys.stdout is None or not hasattr(sys.stdout, "reconfigure"):
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


_configure_console_output()

class AutomaticNASAFramework:
    """Prepare prototype environmental layers and habitat scores."""
    
    def __init__(self, species='great_white', seed=2339):
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError("seed must be an integer")

        self.seed = seed
        self.rng = np.random.default_rng(seed)

        # Credentials are runtime-only. Never commit an Earthdata token.
        self.jwt_token = os.environ.get("EARTHDATA_TOKEN")
        print("🛰️ Shark habitat prototype initialising")

        self.session = requests.Session()

        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'SharkHabitatPrototype/1.0'
        }

        if self.jwt_token:
            self.headers['Authorization'] = f'Bearer {self.jwt_token}'
            print("✅ Earthdata token configured for optional request experiments")
        else:
            print("ℹ️ EARTHDATA_TOKEN is not set; generated prototype mode is available")
        
        # NASA API endpoints
        self.nasa_apis = {
            'cmr_search': 'https://cmr.earthdata.nasa.gov/search/granules.json',
            'giovanni': 'https://giovanni.gsfc.nasa.gov/daac-bin/service_manager.pl',
            'opendap': 'https://oceandata.sci.gsfc.nasa.gov/opendap',
            'direct_download': 'https://oceandata.sci.gsfc.nasa.gov/cgi/getfile'
        }
        
        # NASA collection IDs (real collections)
        self.collections = {
            'modis_sst_monthly': 'C1200034768-OB_DAAC',
            'modis_chl_monthly': 'C1200034764-OB_DAAC',
            'viirs_sst_monthly': 'C1200035558-OB_DAAC',
            'viirs_chl_monthly': 'C1200035554-OB_DAAC'
        }
        
        # Illustrative multi-species parameters for software experiments. They
        # are not a reviewed ecological dataset and do not establish presence.
        self.shark_species_params = {
            'great_white': {
                'name': 'Great White Shark',
                'scientific': 'Carcharodon carcharias',
                'optimal_temp': 18.0,      # Jorgensen et al. 2010
                'temp_tolerance': 3.5,
                'temp_range': (12.0, 24.0),
                'thermal_coeff': 0.08,
                'trophic_level': 4.5,      # Cortés 1999
                'productivity_threshold': 0.8,
                'frontal_affinity': 0.9,   # High affinity for thermal fronts
                'depth_preference': (0, 250),  # meters
                'coastal_affinity': 0.7,   # Moderate coastal preference
                'migration_tendency': 0.9, # High migratory behavior
                'prey_size_preference': 'large',  # Seals, large fish
                'hunting_strategy': 'ambush_predator',
                'metabolic_rate': 'high',
                'habitat_specificity': 'temperate_coastal',
                'prey_preferences': ['seals', 'tuna'],
                'diel_migration': 30,  # meters
                'thermoregulation': 0.7,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.6
            },
            'tiger_shark': {
                'name': 'Tiger Shark',
                'scientific': 'Galeocerdo cuvier',
                'optimal_temp': 25.0,      # Heithaus et al. 2007
                'temp_tolerance': 4.0,
                'temp_range': (20.0, 30.0),
                'thermal_coeff': 0.06,
                'trophic_level': 4.2,      # Cortés 1999
                'productivity_threshold': 0.6,
                'frontal_affinity': 0.6,   # Moderate frontal zone preference
                'depth_preference': (0, 350),  # meters
                'coastal_affinity': 0.9,   # Very high coastal preference
                'migration_tendency': 0.7, # Moderate migratory behavior
                'prey_size_preference': 'varied',  # Opportunistic
                'hunting_strategy': 'generalist_predator',
                'metabolic_rate': 'moderate',
                'habitat_specificity': 'tropical_coastal',
                'prey_preferences': ['rays', 'small_fish', 'tuna'],
                'diel_migration': 40,
                'thermoregulation': 0.5,
                'feeding_efficiency': 0.9,
                'thermocline_affinity': 0.4
            },
            'bull_shark': {
                'name': 'Bull Shark',
                'scientific': 'Carcharhinus leucas',
                'optimal_temp': 27.0,      # Heupel & Simpfendorfer 2008
                'temp_tolerance': 5.0,     # High temperature tolerance
                'temp_range': (22.0, 32.0),
                'thermal_coeff': 0.05,
                'trophic_level': 4.0,      # Cortés 1999
                'productivity_threshold': 0.5,
                'frontal_affinity': 0.4,   # Low frontal zone preference
                'depth_preference': (0, 150),  # meters, shallow preference
                'coastal_affinity': 0.95,  # Extremely high coastal preference
                'migration_tendency': 0.5, # Low migratory behavior
                'prey_size_preference': 'medium',  # Fish, rays
                'hunting_strategy': 'opportunistic_predator',
                'metabolic_rate': 'moderate',
                'habitat_specificity': 'estuarine_coastal',
                'prey_preferences': ['small_fish', 'rays'],
                'diel_migration': 20,  # Less migration
                'thermoregulation': 0.3,
                'feeding_efficiency': 0.7,
                'thermocline_affinity': 0.2
            },
            'hammerhead': {
                'name': 'Great Hammerhead Shark',
                'scientific': 'Sphyrna mokarran',
                'optimal_temp': 24.0,      # Gallagher et al. 2017
                'temp_tolerance': 3.0,
                'temp_range': (21.0, 27.0),
                'thermal_coeff': 0.07,
                'trophic_level': 4.3,      # Cortés 1999
                'productivity_threshold': 0.7,
                'frontal_affinity': 0.8,   # High frontal zone preference
                'depth_preference': (0, 300),  # meters
                'coastal_affinity': 0.8,   # High coastal preference
                'migration_tendency': 0.8, # High migratory behavior
                'prey_size_preference': 'medium',  # Rays, fish
                'hunting_strategy': 'specialized_predator',
                'metabolic_rate': 'high',
                'habitat_specificity': 'tropical_pelagic'
            },
            'mako': {
                'name': 'Shortfin Mako Shark',
                'scientific': 'Isurus oxyrinchus',
                'optimal_temp': 20.0,      # Vaudo et al. 2016
                'temp_tolerance': 4.5,
                'temp_range': (15.0, 25.0),
                'thermal_coeff': 0.09,     # High thermal sensitivity
                'trophic_level': 4.6,      # High trophic level
                'productivity_threshold': 0.9,  # High productivity needs
                'frontal_affinity': 0.95,  # Extremely high frontal affinity
                'depth_preference': (0, 500),  # meters, deep diving
                'coastal_affinity': 0.3,   # Low coastal preference (pelagic)
                'migration_tendency': 0.95, # Extremely high migratory
                'prey_size_preference': 'fast_fish',  # Tuna, billfish
                'hunting_strategy': 'high_speed_predator',
                'metabolic_rate': 'very_high',
                'habitat_specificity': 'pelagic_oceanic'
            },
            'blue_shark': {
                'name': 'Blue Shark',
                'scientific': 'Prionace glauca',
                'optimal_temp': 16.0,      # Queiroz et al. 2005
                'temp_tolerance': 6.0,     # Very high temperature tolerance
                'temp_range': (10.0, 22.0),
                'thermal_coeff': 0.04,     # Low thermal sensitivity
                'trophic_level': 3.8,      # Lower trophic level
                'productivity_threshold': 0.4,  # Low productivity needs
                'frontal_affinity': 0.7,   # Moderate frontal affinity
                'depth_preference': (0, 400),  # meters
                'coastal_affinity': 0.2,   # Very low coastal preference
                'migration_tendency': 0.98, # Extremely high migratory
                'prey_size_preference': 'small_fish',  # Squid, small fish
                'hunting_strategy': 'opportunistic_pelagic',
                'metabolic_rate': 'low',
                'habitat_specificity': 'open_ocean',
                'prey_preferences': ['squid', 'small_fish', 'krill'],
                'diel_migration': 50,
                'thermoregulation': 0.2,
                'feeding_efficiency': 0.6,
                'thermocline_affinity': 0.8
            },
            'whale_shark': {
                'name': 'Whale Shark',
                'scientific': 'Rhincodon typus',
                'optimal_temp': 26.0,      # Sequeira et al. 2014
                'temp_tolerance': 4.0,
                'temp_range': (21.0, 30.0),
                'thermal_coeff': 0.05,
                'trophic_level': 2.1,      # Filter feeder
                'productivity_threshold': 0.9,  # Needs high plankton productivity
                'frontal_affinity': 0.8,   # High affinity for productive fronts
                'depth_preference': (0, 200),  # Surface feeder
                'coastal_affinity': 0.6,   # Moderate coastal preference
                'migration_tendency': 0.9, # Highly migratory
                'prey_size_preference': 'plankton',  # Plankton, small fish
                'hunting_strategy': 'filter_feeder',
                'metabolic_rate': 'low',
                'habitat_specificity': 'tropical_pelagic',
                'prey_preferences': ['plankton', 'krill', 'fish_eggs'],
                'diel_migration': 100,  # Deep diving
                'thermoregulation': 0.4,
                'feeding_efficiency': 0.9,
                'thermocline_affinity': 0.7
            },
            'basking_shark': {
                'name': 'Basking Shark',
                'scientific': 'Cetorhinus maximus',
                'optimal_temp': 14.0,      # Sims et al. 2005
                'temp_tolerance': 5.0,
                'temp_range': (8.0, 20.0),
                'thermal_coeff': 0.06,
                'trophic_level': 2.0,      # Filter feeder
                'productivity_threshold': 0.8,  # Needs high zooplankton
                'frontal_affinity': 0.9,   # Very high frontal affinity
                'depth_preference': (0, 200),  # Surface feeder
                'coastal_affinity': 0.5,   # Moderate coastal preference
                'migration_tendency': 0.95, # Extremely migratory
                'prey_size_preference': 'zooplankton',
                'hunting_strategy': 'filter_feeder',
                'metabolic_rate': 'low',
                'habitat_specificity': 'temperate_pelagic',
                'prey_preferences': ['zooplankton', 'copepods', 'krill'],
                'diel_migration': 80,
                'thermoregulation': 0.3,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.9
            },
            'thresher_shark': {
                'name': 'Common Thresher Shark',
                'scientific': 'Alopias vulpinus',
                'optimal_temp': 19.0,      # Cartamil et al. 2010
                'temp_tolerance': 4.0,
                'temp_range': (14.0, 24.0),
                'thermal_coeff': 0.07,
                'trophic_level': 4.2,
                'productivity_threshold': 0.7,
                'frontal_affinity': 0.8,   # High frontal affinity
                'depth_preference': (0, 500),  # Deep diving capability
                'coastal_affinity': 0.4,   # Low coastal preference
                'migration_tendency': 0.8, # High migratory
                'prey_size_preference': 'schooling_fish',
                'hunting_strategy': 'tail_stunning',
                'metabolic_rate': 'high',
                'habitat_specificity': 'temperate_pelagic',
                'prey_preferences': ['sardines', 'anchovies', 'mackerel'],
                'diel_migration': 200,  # Deep vertical migration
                'thermoregulation': 0.6,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.8
            },
            'nurse_shark': {
                'name': 'Nurse Shark',
                'scientific': 'Ginglymostoma cirratum',
                'optimal_temp': 26.0,      # Morrissey & Gruber 1993
                'temp_tolerance': 3.0,
                'temp_range': (22.0, 30.0),
                'thermal_coeff': 0.04,
                'trophic_level': 3.5,
                'productivity_threshold': 0.5,
                'frontal_affinity': 0.3,   # Low frontal affinity
                'depth_preference': (0, 75),   # Shallow water preference
                'coastal_affinity': 0.95,  # Extremely high coastal preference
                'migration_tendency': 0.2, # Very low migratory
                'prey_size_preference': 'benthic',  # Bottom dwellers
                'hunting_strategy': 'suction_feeder',
                'metabolic_rate': 'low',
                'habitat_specificity': 'tropical_reef',
                'prey_preferences': ['crustaceans', 'mollusks', 'small_fish'],
                'diel_migration': 5,   # Minimal vertical movement
                'thermoregulation': 0.2,
                'feeding_efficiency': 0.7,
                'thermocline_affinity': 0.1
            },
            'reef_shark': {
                'name': 'Caribbean Reef Shark',
                'scientific': 'Carcharhinus perezi',
                'optimal_temp': 27.0,      # Bond et al. 2012
                'temp_tolerance': 3.0,
                'temp_range': (24.0, 30.0),
                'thermal_coeff': 0.05,
                'trophic_level': 4.0,
                'productivity_threshold': 0.6,
                'frontal_affinity': 0.4,   # Low frontal affinity
                'depth_preference': (0, 100),  # Reef depths
                'coastal_affinity': 0.9,   # High coastal preference
                'migration_tendency': 0.3, # Low migratory
                'prey_size_preference': 'reef_fish',
                'hunting_strategy': 'reef_predator',
                'metabolic_rate': 'moderate',
                'habitat_specificity': 'coral_reef',
                'prey_preferences': ['reef_fish', 'rays', 'crustaceans'],
                'diel_migration': 15,
                'thermoregulation': 0.3,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.2
            },
            'lemon_shark': {
                'name': 'Lemon Shark',
                'scientific': 'Negaprion brevirostris',
                'optimal_temp': 26.0,      # Morrissey & Gruber 1993
                'temp_tolerance': 4.0,
                'temp_range': (20.0, 30.0),
                'thermal_coeff': 0.06,
                'trophic_level': 4.1,
                'productivity_threshold': 0.6,
                'frontal_affinity': 0.5,   # Moderate frontal affinity
                'depth_preference': (0, 90),   # Shallow coastal
                'coastal_affinity': 0.9,   # High coastal preference
                'migration_tendency': 0.6, # Moderate migratory
                'prey_size_preference': 'medium_fish',
                'hunting_strategy': 'active_predator',
                'metabolic_rate': 'moderate',
                'habitat_specificity': 'mangrove_coastal',
                'prey_preferences': ['bonefish', 'rays', 'crustaceans'],
                'diel_migration': 25,
                'thermoregulation': 0.4,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.3
            },
            'blacktip_shark': {
                'name': 'Blacktip Shark',
                'scientific': 'Carcharhinus limbatus',
                'optimal_temp': 25.0,      # Heupel & Hueter 2002
                'temp_tolerance': 4.0,
                'temp_range': (20.0, 30.0),
                'thermal_coeff': 0.06,
                'trophic_level': 4.0,
                'productivity_threshold': 0.6,
                'frontal_affinity': 0.6,   # Moderate frontal affinity
                'depth_preference': (0, 100),  # Shallow coastal
                'coastal_affinity': 0.85,  # High coastal preference
                'migration_tendency': 0.7, # High migratory
                'prey_size_preference': 'schooling_fish',
                'hunting_strategy': 'fast_pursuit',
                'metabolic_rate': 'high',
                'habitat_specificity': 'tropical_coastal',
                'prey_preferences': ['sardines', 'herrings', 'anchovies'],
                'diel_migration': 30,
                'thermoregulation': 0.5,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.4
            },
            'sandbar_shark': {
                'name': 'Sandbar Shark',
                'scientific': 'Carcharhinus plumbeus',
                'optimal_temp': 22.0,      # Grubbs et al. 2007
                'temp_tolerance': 5.0,
                'temp_range': (16.0, 28.0),
                'thermal_coeff': 0.05,
                'trophic_level': 4.0,
                'productivity_threshold': 0.5,
                'frontal_affinity': 0.4,   # Low frontal affinity
                'depth_preference': (20, 280),  # Continental shelf
                'coastal_affinity': 0.8,   # High coastal preference
                'migration_tendency': 0.8, # High migratory
                'prey_size_preference': 'bottom_fish',
                'hunting_strategy': 'bottom_predator',
                'metabolic_rate': 'moderate',
                'habitat_specificity': 'continental_shelf',
                'prey_preferences': ['bottom_fish', 'rays', 'crabs'],
                'diel_migration': 40,
                'thermoregulation': 0.4,
                'feeding_efficiency': 0.7,
                'thermocline_affinity': 0.3
            },
            'spinner_shark': {
                'name': 'Spinner Shark',
                'scientific': 'Carcharhinus brevipinna',
                'optimal_temp': 24.0,      # Burgess & Branstetter 2009
                'temp_tolerance': 4.0,
                'temp_range': (19.0, 29.0),
                'thermal_coeff': 0.06,
                'trophic_level': 4.1,
                'productivity_threshold': 0.7,
                'frontal_affinity': 0.7,   # High frontal affinity
                'depth_preference': (0, 100),  # Surface to moderate depth
                'coastal_affinity': 0.7,   # Moderate coastal preference
                'migration_tendency': 0.8, # High migratory
                'prey_size_preference': 'schooling_fish',
                'hunting_strategy': 'spinning_attack',
                'metabolic_rate': 'high',
                'habitat_specificity': 'warm_coastal',
                'prey_preferences': ['sardines', 'herrings', 'rays'],
                'diel_migration': 35,
                'thermoregulation': 0.5,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.5
            },
            'dusky_shark': {
                'name': 'Dusky Shark',
                'scientific': 'Carcharhinus obscurus',
                'optimal_temp': 20.0,      # Musick et al. 1993
                'temp_tolerance': 6.0,
                'temp_range': (15.0, 28.0),
                'thermal_coeff': 0.05,
                'trophic_level': 4.2,
                'productivity_threshold': 0.6,
                'frontal_affinity': 0.6,   # Moderate frontal affinity
                'depth_preference': (0, 400),  # Wide depth range
                'coastal_affinity': 0.6,   # Moderate coastal preference
                'migration_tendency': 0.9, # Very high migratory
                'prey_size_preference': 'large_fish',
                'hunting_strategy': 'pursuit_predator',
                'metabolic_rate': 'moderate',
                'habitat_specificity': 'temperate_coastal',
                'prey_preferences': ['bluefish', 'tuna', 'rays'],
                'diel_migration': 50,
                'thermoregulation': 0.5,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.6
            },
            'silky_shark': {
                'name': 'Silky Shark',
                'scientific': 'Carcharhinus falciformis',
                'optimal_temp': 24.0,      # Bonfil et al. 2005
                'temp_tolerance': 4.0,
                'temp_range': (20.0, 28.0),
                'thermal_coeff': 0.06,
                'trophic_level': 4.3,
                'productivity_threshold': 0.7,
                'frontal_affinity': 0.8,   # High frontal affinity
                'depth_preference': (0, 500),  # Pelagic, deep diving
                'coastal_affinity': 0.3,   # Low coastal preference
                'migration_tendency': 0.9, # Very high migratory
                'prey_size_preference': 'pelagic_fish',
                'hunting_strategy': 'pelagic_predator',
                'metabolic_rate': 'high',
                'habitat_specificity': 'tropical_pelagic',
                'prey_preferences': ['tuna', 'squid', 'flying_fish'],
                'diel_migration': 100,
                'thermoregulation': 0.6,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.7
            },
            'porbeagle_shark': {
                'name': 'Porbeagle Shark',
                'scientific': 'Lamna nasus',
                'optimal_temp': 12.0,      # Campana et al. 2010
                'temp_tolerance': 6.0,
                'temp_range': (5.0, 18.0),
                'thermal_coeff': 0.08,
                'trophic_level': 4.4,
                'productivity_threshold': 0.8,
                'frontal_affinity': 0.9,   # Very high frontal affinity
                'depth_preference': (0, 700),  # Deep diving capability
                'coastal_affinity': 0.4,   # Low coastal preference
                'migration_tendency': 0.9, # Very high migratory
                'prey_size_preference': 'fast_fish',
                'hunting_strategy': 'endothermic_predator',
                'metabolic_rate': 'very_high',
                'habitat_specificity': 'cold_pelagic',
                'prey_preferences': ['mackerel', 'herring', 'squid'],
                'diel_migration': 150,
                'thermoregulation': 0.8,  # Endothermic
                'feeding_efficiency': 0.9,
                'thermocline_affinity': 0.8
            }
        }

        # Add additional major species to expand coverage
        additional_species = {
            'longfin_mako': {
                'name': 'Longfin Mako Shark',
                'scientific': 'Isurus paucus',
                'optimal_temp': 18.0,
                'temp_tolerance': 3.0,
                'temp_range': (13.0, 23.0),
                'thermal_coeff': 0.12,
                'trophic_level': 4.3,
                'productivity_threshold': 0.7,
                'frontal_affinity': 0.8,
                'depth_preference': (0, 220),
                'coastal_affinity': 0.3,
                'migration_tendency': 0.9,
                'prey_size_preference': 'large_fish',
                'hunting_strategy': 'endothermic_predator',
                'metabolic_rate': 'very_high',
                'habitat_specificity': 'tropical_pelagic',
                'prey_preferences': ['tuna', 'billfish', 'squid'],
                'diel_migration': 200,
                'thermoregulation': 0.7,
                'feeding_efficiency': 0.85,
                'thermocline_affinity': 0.7
            },
            'salmon_shark': {
                'name': 'Salmon Shark',
                'scientific': 'Lamna ditropis',
                'optimal_temp': 10.0,
                'temp_tolerance': 3.0,
                'temp_range': (5.0, 15.0),
                'thermal_coeff': 0.08,
                'trophic_level': 4.1,
                'productivity_threshold': 0.9,
                'frontal_affinity': 0.9,
                'depth_preference': (0, 255),
                'coastal_affinity': 0.6,
                'migration_tendency': 0.8,
                'prey_size_preference': 'fast_fish',
                'hunting_strategy': 'endothermic_predator',
                'metabolic_rate': 'very_high',
                'habitat_specificity': 'cold_pelagic',
                'prey_preferences': ['salmon', 'herring', 'squid'],
                'diel_migration': 100,
                'thermoregulation': 0.8,
                'feeding_efficiency': 0.9,
                'thermocline_affinity': 0.8
            },
            'sand_tiger': {
                'name': 'Sand Tiger Shark',
                'scientific': 'Carcharias taurus',
                'optimal_temp': 20.0,
                'temp_tolerance': 4.0,
                'temp_range': (15.0, 25.0),
                'thermal_coeff': 0.06,
                'trophic_level': 4.0,
                'productivity_threshold': 0.6,
                'frontal_affinity': 0.5,
                'depth_preference': (0, 190),
                'coastal_affinity': 0.8,
                'migration_tendency': 0.6,
                'prey_size_preference': 'medium_fish',
                'hunting_strategy': 'ambush_predator',
                'metabolic_rate': 'moderate',
                'habitat_specificity': 'temperate_coastal',
                'prey_preferences': ['bony_fish', 'rays', 'crustaceans'],
                'diel_migration': 50,
                'thermoregulation': 0.0,
                'feeding_efficiency': 0.7,
                'thermocline_affinity': 0.4
            },
            'scalloped_hammerhead': {
                'name': 'Scalloped Hammerhead',
                'scientific': 'Sphyrna lewini',
                'optimal_temp': 23.0,
                'temp_tolerance': 4.0,
                'temp_range': (18.0, 28.0),
                'thermal_coeff': 0.08,
                'trophic_level': 4.2,
                'productivity_threshold': 0.7,
                'frontal_affinity': 0.8,
                'depth_preference': (0, 275),
                'coastal_affinity': 0.7,
                'migration_tendency': 0.9,
                'prey_size_preference': 'schooling_fish',
                'hunting_strategy': 'electroreception_predator',
                'metabolic_rate': 'high',
                'habitat_specificity': 'tropical_coastal',
                'prey_preferences': ['schooling_fish', 'squid', 'rays'],
                'diel_migration': 100,
                'thermoregulation': 0.0,
                'feeding_efficiency': 0.8,
                'thermocline_affinity': 0.6
            },
            'smooth_hammerhead': {
                'name': 'Smooth Hammerhead',
                'scientific': 'Sphyrna zygaena',
                'optimal_temp': 20.0,
                'temp_tolerance': 4.0,
                'temp_range': (15.0, 25.0),
                'thermal_coeff': 0.07,
                'trophic_level': 4.1,
                'productivity_threshold': 0.6,
                'frontal_affinity': 0.7,
                'depth_preference': (0, 200),
                'coastal_affinity': 0.6,
                'migration_tendency': 0.8,
                'prey_size_preference': 'schooling_fish',
                'hunting_strategy': 'electroreception_predator',
                'metabolic_rate': 'high',
                'habitat_specificity': 'temperate_coastal',
                'prey_preferences': ['sardines', 'anchovies', 'squid'],
                'diel_migration': 80,
                'thermoregulation': 0.0,
                'feeding_efficiency': 0.75,
                'thermocline_affinity': 0.5
            },
            'bonnethead_shark': {
                'name': 'Bonnethead Shark',
                'scientific': 'Sphyrna tiburo',
                'optimal_temp': 25.0,
                'temp_tolerance': 3.0,
                'temp_range': (20.0, 30.0),
                'thermal_coeff': 0.09,
                'trophic_level': 3.5,
                'productivity_threshold': 0.5,
                'frontal_affinity': 0.4,
                'depth_preference': (0, 25),
                'coastal_affinity': 0.9,
                'migration_tendency': 0.4,
                'prey_size_preference': 'small_prey',
                'hunting_strategy': 'benthic_forager',
                'metabolic_rate': 'moderate',
                'habitat_specificity': 'shallow_warm',
                'prey_preferences': ['crabs', 'shrimp', 'small_fish'],
                'diel_migration': 10,
                'thermoregulation': 0.0,
                'feeding_efficiency': 0.6,
                'thermocline_affinity': 0.2
            }
        }

        # Merge additional species into main dictionary
        self.shark_species_params.update(additional_species)

        # Select a known prototype profile.
        if species in self.shark_species_params:
            self.current_species = species
            self.shark_params = self.shark_species_params[self.current_species]
            print(f"🦈 Species set to: {self.shark_params['name']} ({self.shark_params['scientific']})")
        else:
            print(f"❌ Unknown species '{species}', defaulting to 'great_white'")
            print(f"Available species: {list(self.shark_species_params.keys())}")
            self.current_species = 'great_white'
            self.shark_params = self.shark_species_params[self.current_species]

        # Bathymetry data source (GEBCO/ETOPO)
        self.bathymetry_api = 'https://www.gebco.net/data_and_products/gebco_web_services/web_map_service/'

        # Initialize ecological models
        self.prey_models = self._initialize_prey_models()
        self.predator_interactions = self._initialize_predator_interactions()
        self.human_impacts = self._initialize_human_impact_models()
        self.temporal_factors = self._initialize_temporal_factors()

        # Initialize additional heuristic components.
        self.ocean_dynamics = self._initialize_ocean_dynamics()
        self.water_quality = self._initialize_water_quality()
        self.weather_effects = self._initialize_weather_effects()

    def set_species(self, species_key):
        """Change the target shark species"""
        if species_key in self.shark_species_params:
            self.current_species = species_key
            self.shark_params = self.shark_species_params[species_key]
            print(f"🦈 Species set to: {self.shark_params['name']} ({self.shark_params['scientific']})")
            return True
        else:
            print(f"❌ Unknown species: {species_key}")
            print(f"Available species: {list(self.shark_species_params.keys())}")
            return False

    def get_available_species(self):
        """Get list of available species"""
        return list(self.shark_species_params.keys())

    @property
    def species_params(self):
        """Alias for shark_species_params for compatibility"""
        return self.shark_species_params

    def get_available_species(self):
        """Get list of available shark species"""
        return {key: params['name'] for key, params in self.shark_species_params.items()}



    def _authenticate_nasa(self):
        """Configure authentication for experimental Earthdata requests."""
        print("🔐 AUTHENTICATING WITH NASA EARTHDATA...")

        if self.jwt_token:
            print("   ✅ Earthdata token configured for authenticated requests")
            self.authenticated = True
            return True
        else:
            print("   ❌ No NASA JWT token available")
            print("   🔑 Please provide a valid NASA Earthdata JWT token")
            self.authenticated = False
            return False

    def explain_species_differentiation(self):
        """Explain how the prototype's species profiles differ."""
        print("\n🔬 SPECIES DIFFERENTIATION METHODOLOGY")
        print("=" * 60)

        print("\n📊 KEY DIFFERENTIATION PARAMETERS:")
        print("1. THERMAL PREFERENCES:")
        for key, params in self.shark_species_params.items():
            print(f"   {params['name']}: {params['optimal_temp']}°C (±{params['temp_tolerance']}°C)")

        print("\n2. HABITAT SPECIALIZATION:")
        for key, params in self.shark_species_params.items():
            print(f"   {params['name']}: {params['habitat_specificity']}")

        print("\n3. ECOLOGICAL NICHES:")
        for key, params in self.shark_species_params.items():
            print(f"   {params['name']}: {params['hunting_strategy']} (TL: {params['trophic_level']})")

        print("\n4. BEHAVIORAL PATTERNS:")
        for key, params in self.shark_species_params.items():
            coastal = params['coastal_affinity']
            migration = params['migration_tendency']
            print(f"   {params['name']}: Coastal={coastal:.1f}, Migration={migration:.1f}")

        return self.shark_species_params

    def _initialize_prey_models(self):
        """Initialize prey distribution models"""
        return {
            'seals': {
                'optimal_temp': 15.0,
                'temp_range': (10.0, 20.0),
                'coastal_affinity': 0.95,
                'depth_preference': (0, 50),
                'seasonal_abundance': {'winter': 0.8, 'spring': 1.2, 'summer': 1.0, 'fall': 0.9}
            },
            'tuna': {
                'optimal_temp': 20.0,
                'temp_range': (15.0, 25.0),
                'pelagic_affinity': 0.9,
                'depth_preference': (0, 200),
                'seasonal_abundance': {'winter': 0.7, 'spring': 1.1, 'summer': 1.3, 'fall': 0.9}
            },
            'rays': {
                'optimal_temp': 22.0,
                'temp_range': (18.0, 28.0),
                'benthic_affinity': 0.9,
                'depth_preference': (10, 100),
                'seasonal_abundance': {'winter': 0.6, 'spring': 1.0, 'summer': 1.4, 'fall': 1.0}
            },
            'small_fish': {
                'optimal_temp': 18.0,
                'temp_range': (12.0, 24.0),
                'schooling_factor': 2.0,
                'depth_preference': (0, 150),
                'seasonal_abundance': {'winter': 0.8, 'spring': 1.3, 'summer': 1.1, 'fall': 0.8}
            }
        }

    def _initialize_predator_interactions(self):
        """Initialize predator-predator interaction models"""
        return {
            'competitive_exclusion': {
                'great_white_tiger': 0.3,  # Great whites dominate
                'great_white_bull': 0.2,
                'tiger_bull': 0.1,
                'mako_blue': 0.05,  # Minimal competition (different niches)
                'hammerhead_tiger': 0.15
            },
            'killer_whale_avoidance': {
                'great_white': 0.8,  # High avoidance
                'tiger_shark': 0.6,
                'bull_shark': 0.4,
                'hammerhead': 0.7,
                'mako': 0.9,  # Highest avoidance
                'blue_shark': 0.5,
                'whale_shark': 0.3,  # Large size, less avoidance
                'basking_shark': 0.2,  # Large filter feeder
                'thresher_shark': 0.7,
                'nurse_shark': 0.3,  # Bottom dweller
                'reef_shark': 0.5,
                'lemon_shark': 0.5,
                'blacktip_shark': 0.6,
                'sandbar_shark': 0.5,
                'spinner_shark': 0.6,
                'dusky_shark': 0.6,
                'silky_shark': 0.7,
                'porbeagle_shark': 0.8,  # Similar to mako
                'longfin_mako': 0.9,  # Similar to shortfin mako
                'salmon_shark': 0.8,  # Endothermic, similar to great white
                'sand_tiger': 0.5,
                'scalloped_hammerhead': 0.7,  # Similar to great hammerhead
                'smooth_hammerhead': 0.7,
                'bonnethead_shark': 0.4  # Smaller, less targeted
            },
            'size_based_dominance': {
                'adult_juvenile_exclusion': 0.4,
                'territorial_radius': 5.0  # km
            }
        }

    def _initialize_human_impact_models(self):
        """Initialize human impact models"""
        return {
            'fishing_pressure': {
                'commercial_longline': {'mortality_rate': 0.15, 'avoidance_distance': 10},
                'commercial_gillnet': {'mortality_rate': 0.25, 'avoidance_distance': 5},
                'recreational': {'mortality_rate': 0.05, 'avoidance_distance': 2},
                'shark_finning': {'mortality_rate': 0.9, 'avoidance_distance': 20}
            },
            'marine_traffic': {
                'shipping_lanes': {'disturbance_radius': 2, 'avoidance_factor': 0.3},
                'recreational_boats': {'disturbance_radius': 0.5, 'avoidance_factor': 0.1},
                'fishing_vessels': {'disturbance_radius': 1, 'avoidance_factor': 0.2}
            },
            'pollution': {
                'plastic_debris': {'habitat_degradation': 0.1},
                'chemical_runoff': {'habitat_degradation': 0.2},
                'noise_pollution': {'behavioral_impact': 0.15}
            }
        }

    def _initialize_temporal_factors(self):
        """Initialize temporal factor models"""
        return {
            'lunar_cycles': {
                'new_moon': {'feeding_activity': 1.2, 'movement_activity': 0.8},
                'full_moon': {'feeding_activity': 1.4, 'movement_activity': 1.2},
                'quarter_moon': {'feeding_activity': 1.0, 'movement_activity': 1.0}
            },
            'tidal_effects': {
                'high_tide': {'coastal_access': 1.3, 'feeding_opportunity': 1.1},
                'low_tide': {'coastal_access': 0.7, 'feeding_opportunity': 0.9},
                'tidal_change': {'feeding_opportunity': 1.2}
            },
            'seasonal_behavior': {
                'breeding_season': {'habitat_shift': 0.8, 'feeding_reduction': 0.7},
                'pupping_season': {'shallow_preference': 1.5, 'territorial_behavior': 1.3},
                'migration_season': {'movement_increase': 2.0, 'feeding_opportunistic': 1.1}
            }
        }

    def _initialize_ocean_dynamics(self):
        """Initialize ocean dynamics system"""
        return {
            'current_systems': {
                'california_current': {
                    'velocity_u': -0.15,  # m/s eastward
                    'velocity_v': -0.25,  # m/s northward
                    'seasonal_variation': 0.3,
                    'depth_profile': 'exponential_decay'
                },
                'gulf_stream': {
                    'velocity_u': 1.2,
                    'velocity_v': 0.8,
                    'seasonal_variation': 0.2,
                    'depth_profile': 'linear_decay'
                }
            },
            'upwelling_zones': {
                'california_coast': {
                    'strength': 0.8,  # relative intensity
                    'seasonal_peak': 'summer',
                    'nutrient_enhancement': 2.5,
                    'temperature_depression': -2.0  # °C
                },
                'peru_coast': {
                    'strength': 1.0,
                    'seasonal_peak': 'winter',
                    'nutrient_enhancement': 3.0,
                    'temperature_depression': -3.5
                }
            },
            'mesoscale_eddies': {
                'warm_core_eddies': {
                    'temperature_anomaly': 2.0,  # °C
                    'productivity_effect': -0.3,  # reduced productivity
                    'typical_radius': 50,  # km
                    'lifespan': 90  # days
                },
                'cold_core_eddies': {
                    'temperature_anomaly': -1.5,
                    'productivity_effect': 0.5,  # enhanced productivity
                    'typical_radius': 40,
                    'lifespan': 120
                }
            }
        }

    def _initialize_water_quality(self):
        """Initialize water quality parameters"""
        return {
            'dissolved_oxygen': {
                'surface_concentration': 8.5,  # mg/L
                'thermocline_reduction': 0.3,  # factor
                'omz_depth_range': [200, 1000],  # meters
                'omz_concentration': 2.0,  # mg/L
                'species_tolerance': {
                    'great_white': {'min_oxygen': 4.0, 'optimal': 6.5},
                    'tiger_shark': {'min_oxygen': 3.5, 'optimal': 6.0},
                    'bull_shark': {'min_oxygen': 3.0, 'optimal': 5.5},
                    'mako': {'min_oxygen': 4.5, 'optimal': 7.0},
                    'blue_shark': {'min_oxygen': 3.8, 'optimal': 6.2},
                    'hammerhead': {'min_oxygen': 4.2, 'optimal': 6.8}
                }
            },
            'salinity': {
                'open_ocean': 35.0,  # psu
                'coastal_variation': 2.0,  # psu range
                'estuarine_gradient': [0, 35],  # freshwater to marine
                'species_tolerance': {
                    'bull_shark': {'min_salinity': 0, 'max_salinity': 40, 'optimal': 15},
                    'great_white': {'min_salinity': 30, 'max_salinity': 38, 'optimal': 35},
                    'tiger_shark': {'min_salinity': 25, 'max_salinity': 38, 'optimal': 34}
                }
            },
            'ph_levels': {
                'surface_ph': 8.1,
                'deep_water_ph': 7.8,
                'acidification_trend': -0.002,  # per year
                'species_sensitivity': {
                    'great_white': {'min_ph': 7.6, 'optimal': 8.0},
                    'tiger_shark': {'min_ph': 7.5, 'optimal': 7.9}
                }
            },
            'turbidity': {
                'clear_water': 0.5,  # NTU
                'coastal_turbidity': 5.0,
                'river_plume': 20.0,
                'hunting_efficiency': {
                    'visual_predators': {'optimal_turbidity': 2.0, 'max_turbidity': 10.0},
                    'electroreception': {'turbidity_independence': 0.9}
                }
            }
        }

    def _initialize_weather_effects(self):
        """Initialize weather and storm effects"""
        return {
            'storm_systems': {
                'hurricane_categories': {
                    'cat_1': {'wind_speed': 33, 'displacement_radius': 100, 'depth_refuge': 50},
                    'cat_2': {'wind_speed': 43, 'displacement_radius': 150, 'depth_refuge': 75},
                    'cat_3': {'wind_speed': 50, 'displacement_radius': 200, 'depth_refuge': 100},
                    'cat_4': {'wind_speed': 58, 'displacement_radius': 300, 'depth_refuge': 150},
                    'cat_5': {'wind_speed': 70, 'displacement_radius': 500, 'depth_refuge': 200}
                },
                'species_responses': {
                    'great_white': {'storm_avoidance': 0.8, 'deep_refuge': 0.7},
                    'tiger_shark': {'storm_avoidance': 0.6, 'deep_refuge': 0.5},
                    'bull_shark': {'storm_avoidance': 0.4, 'deep_refuge': 0.3}
                }
            },
            'wind_effects': {
                'mixing_thresholds': {
                    'light_mixing': 5,   # m/s wind speed
                    'moderate_mixing': 10,
                    'strong_mixing': 15,
                    'extreme_mixing': 25
                },
                'mixed_layer_depth': {
                    'calm': 20,      # meters
                    'light': 35,
                    'moderate': 50,
                    'strong': 75,
                    'extreme': 100
                },
                'thermocline_disruption': {
                    'threshold_wind': 12,  # m/s
                    'disruption_factor': 0.6
                }
            },
            'seasonal_patterns': {
                'winter_storms': {
                    'frequency': 0.3,  # storms per week
                    'intensity_factor': 1.2,
                    'duration': 3  # days average
                },
                'summer_calms': {
                    'frequency': 0.1,
                    'intensity_factor': 0.8,
                    'duration': 1
                }
            }
        }

    def auto_download_nasa_data(self, study_area, date_range, *, lookup_metadata=False):
        """Prepare prototype grids, optionally adding a NASA CMR catalog lookup.

        The historical method name is retained for compatibility. The default
        path is fully local and generated; setting ``lookup_metadata=True``
        queries catalog metadata but still does not turn the grids into
        satellite measurements.
        """

        print("🛰️ PROTOTYPE GRID PREPARATION")
        print("=" * 50)
        print(f"📍 Study Area: {study_area['name']}")
        print(f"📅 Date Range: {date_range[0]} to {date_range[1]}")

        if lookup_metadata:
            if self.jwt_token:
                print("🔑 Using EARTHDATA_TOKEN for authenticated requests")
            else:
                print("ℹ️ Continuing without authenticated Earthdata access")

        if not lookup_metadata:
            metadata_status = {
                'metadata_lookup': 'skipped',
                'evidence_boundary': (
                    'Environmental grids are deterministic generated inputs, '
                    'not satellite measurements.'
                ),
            }
            print("ℹ️ NASA CMR metadata lookup skipped (default prototype mode)")
            bathymetry_data = self._prepare_prototype_bathymetry_data(study_area)
            environmental_data = self._build_prototype_environmental_data(
                study_area, bathymetry_data
            )
            return environmental_data, metadata_status

        # Search for available data
        bbox = f"{study_area['bounds'][0]},{study_area['bounds'][1]},{study_area['bounds'][2]},{study_area['bounds'][3]}"
        temporal = f"{date_range[0]}T00:00:00Z,{date_range[1]}T23:59:59Z"

        real_data = {
            'evidence_boundary': (
                'CMR search results are metadata. Generated fallback grids are '
                'prototype inputs, not satellite measurements.'
            )
        }
        
        # Try to get SST data
        print("\n🌡️ Searching for Sea Surface Temperature data...")
        sst_params = {
            'collection_concept_id': self.collections['modis_sst_monthly'],
            'temporal': temporal,
            'bounding_box': bbox,
            'page_size': 10
        }
        
        try:
            sst_response = requests.get(
                self.nasa_apis['cmr_search'],
                params=sst_params,
                headers=self.headers,
                timeout=30
            )
            
            if sst_response.status_code == 200:
                sst_data = sst_response.json()
                sst_granules = sst_data.get('feed', {}).get('entry', [])
                print(f"   ✅ Found {len(sst_granules)} SST granules")
                real_data['sst_granules'] = len(sst_granules)
                real_data['sst_available'] = True
            else:
                print(f"   ⚠️ SST search returned HTTP {sst_response.status_code}")
                real_data['sst_available'] = False
                
        except Exception as e:
            print(f"   ⚠️ SST search error: {e}")
            real_data['sst_available'] = False
        
        # Try to get Chlorophyll data
        print("\n🌱 Searching for Chlorophyll-a data...")
        chl_params = {
            'collection_concept_id': self.collections['modis_chl_monthly'],
            'temporal': temporal,
            'bounding_box': bbox,
            'page_size': 10
        }
        
        try:
            chl_response = requests.get(
                self.nasa_apis['cmr_search'],
                params=chl_params,
                headers=self.headers,
                timeout=30
            )
            
            if chl_response.status_code == 200:
                chl_data = chl_response.json()
                chl_granules = chl_data.get('feed', {}).get('entry', [])
                print(f"   ✅ Found {len(chl_granules)} Chlorophyll granules")
                real_data['chl_granules'] = len(chl_granules)
                real_data['chl_available'] = True
            else:
                print(f"   ⚠️ Chlorophyll search returned HTTP {chl_response.status_code}")
                real_data['chl_available'] = False
                
        except Exception as e:
            print(f"   ⚠️ Chlorophyll search error: {e}")
            real_data['chl_available'] = False
        
        # The current workflow requires matching SST metadata before continuing.
        if not real_data.get('sst_available'):
            print("❌ No matching SST metadata found; prototype grid not created")
            print("🔑 Check the date, bounds, network, and Earthdata configuration")
            return None, real_data

        if not real_data.get('chl_available'):
            print("⚠️ NASA Chlorophyll data not available - will use SST-based productivity estimates")

        print(f"\n🌊 Preparing bathymetry input...")
        bathymetry_data = self._prepare_prototype_bathymetry_data(study_area)

        print(f"\n📊 Preparing environmental prototype grids...")
        environmental_data = self._build_prototype_environmental_data(
            study_area, bathymetry_data
        )

        return environmental_data, real_data

    def _process_sst_granules(self, granules, bounds, grid_size):
        """Generate a deterministic SST demo grid."""
        try:
            # For now, create a realistic grid based on granule metadata
            # In a full implementation, you would download and process the actual NetCDF files

            grid = []
            lats = np.linspace(bounds[1], bounds[3], grid_size)
            lons = np.linspace(bounds[0], bounds[2], grid_size)

            # Use granule information to create realistic SST values
            base_temp = 15.0  # Default temperature

            # Extract temperature info from granule metadata if available
            for granule in granules[:3]:  # Use first few granules
                title = granule.get('title', '')
                if 'SST' in title:
                    # Extract any temperature hints from metadata
                    pass

            for i, lat in enumerate(lats):
                row = []
                for j, lon in enumerate(lons):
                    # Create realistic SST based on location
                    temp = base_temp + (30 - abs(lat)) * 0.3  # Latitude effect
                    temp += self.rng.normal(0, 1.0)  # Seeded demo variation
                    temp = max(5, min(35, temp))  # Realistic range
                    row.append(temp)
                grid.append(row)

            return grid

        except Exception as e:
            print(f"      Error processing SST granules: {e}")
            return None

    def _process_chl_granules(self, granules, bounds, grid_size):
        """Generate a deterministic chlorophyll demo grid."""
        try:
            grid = []
            lats = np.linspace(bounds[1], bounds[3], grid_size)
            lons = np.linspace(bounds[0], bounds[2], grid_size)

            for i, lat in enumerate(lats):
                row = []
                for j, lon in enumerate(lons):
                    # Create realistic chlorophyll based on location
                    coastal_distance = min(abs(lon - bounds[0]), abs(lon - bounds[2]))

                    if coastal_distance < 1:  # Coastal waters
                        chl = 2.0 + self.rng.exponential(1.0)
                    else:  # Open ocean
                        chl = 0.3 + self.rng.exponential(0.2)

                    chl = max(0.01, min(50, chl))
                    row.append(chl)
                grid.append(row)

            return grid

        except Exception as e:
            print(f"      Error processing Chlorophyll granules: {e}")
            return None

    def _process_bathymetry_response(self, response, bounds):
        """Generate a deterministic bathymetry demo grid."""
        try:
            # Create realistic bathymetry grid
            grid_size = 25
            grid = []

            lats = np.linspace(bounds[1], bounds[3], grid_size)
            lons = np.linspace(bounds[0], bounds[2], grid_size)

            for i, lat in enumerate(lats):
                row = []
                for j, lon in enumerate(lons):
                    # Create realistic depth based on distance from coast
                    coastal_distance = min(abs(lon - bounds[0]), abs(lon - bounds[2]))

                    if coastal_distance < 0.5:  # Very close to coast
                        depth = -self.rng.uniform(10, 100)
                    elif coastal_distance < 2:  # Continental shelf
                        depth = -self.rng.uniform(100, 500)
                    else:  # Deep ocean
                        depth = -self.rng.uniform(1000, 4000)

                    row.append(depth)
                grid.append(row)

            return {
                'depth_data': grid,
                'source': 'Deterministic generated bathymetry prototype',
                'resolution': f'{grid_size}x{grid_size} demo grid',
                'quality': 'Unvalidated generated values'
            }

        except Exception as e:
            print(f"      Error processing bathymetry: {e}")
            return None

    def _estimate_productivity_from_sst(self, sst_data, bounds, grid_size):
        """Estimate a prototype productivity layer from the supplied SST grid."""
        print("      🔄 Estimating a prototype productivity layer from SST...")

        try:
            chl_grid = []

            for i, sst_row in enumerate(sst_data):
                chl_row = []
                for j, sst_temp in enumerate(sst_row):
                    # Use real SST to estimate productivity (Eppley relationship)
                    # Productivity increases with temperature up to optimal range
                    if sst_temp < 15:  # Cold water
                        base_productivity = 0.2
                    elif sst_temp < 25:  # Temperate water
                        base_productivity = 0.5 + (sst_temp - 15) * 0.1
                    else:  # Warm water
                        base_productivity = 1.5 - (sst_temp - 25) * 0.05

                    # Add coastal effects
                    lat_idx = i / (grid_size - 1)
                    lon_idx = j / (grid_size - 1)

                    # Distance from coast effect
                    coastal_distance = min(lon_idx, 1 - lon_idx)
                    coastal_boost = 2.0 * np.exp(-coastal_distance * 5)

                    chl = base_productivity + coastal_boost
                    chl = max(0.01, min(10.0, chl))
                    chl_row.append(chl)

                chl_grid.append(chl_row)

            print("      ✅ Prototype productivity layer estimated from SST")
            return chl_grid

        except Exception as e:
            print(f"      ❌ Error estimating productivity: {e}")
            return None

    def _experimental_sst_grid(self, bounds, grid_size):
        """Attempt an experimental MODIS SST extraction, with demo fallback."""
        print("      🔄 Downloading NASA MODIS Aqua SST data...")

        try:
            # NASA CMR search for MODIS Aqua SST
            params = {
                'collection_concept_id': 'C1996881146-POCLOUD',  # MODIS Aqua L3 SST
                'temporal': '2024-01-01T00:00:00Z,2024-01-31T23:59:59Z',
                'bounding_box': f"{bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]}",
                'page_size': 10
            }

            response = requests.get(
                'https://cmr.earthdata.nasa.gov/search/granules.json',
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                granules = data.get('feed', {}).get('entry', [])

                if granules:
                    print(f"      ✅ Found {len(granules)} NASA SST granules")

                    # Try enhanced NetCDF processing first
                    try:
                        import xarray as xr

                        # Process first few granules with full NetCDF if possible
                        for granule in granules[:3]:  # Try up to 3 granules
                            netcdf_data = self._process_netcdf_granule(granule, bounds, 'sst')
                            if netcdf_data:
                                print(f"      ✅ Enhanced NetCDF processing successful")
                                # Convert to expected grid format
                                return self._convert_netcdf_to_grid(netcdf_data, bounds, grid_size)

                        print(f"      ✅ Using NASA metadata approach (optimized for large datasets)")

                    except ImportError:
                        print(f"      ⚠️ xarray not available, using metadata approach")
                    except Exception as e:
                        print(f"      ⚠️ NetCDF processing error: {e}, using metadata approach")

                    # Fallback to metadata-based processing
                    return self._process_sst_granules(granules, bounds, grid_size)
                else:
                    print("      ❌ No NASA SST granules found")
                    return None
            else:
                print(f"      ❌ NASA CMR error: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"      ❌ SST download error: {e}")
            return None

    def _process_netcdf_granule(self, granule, bounds, variable):
        """Process individual NetCDF granule with full data extraction"""
        try:
            import xarray as xr
            import tempfile
            import os

            # Get download URL from granule metadata
            download_url = self._extract_download_url(granule)
            if not download_url:
                return None

            print(f"         🔄 Processing NetCDF granule...")

            # For OPeNDAP, we can access directly without downloading
            if 'opendap' in download_url.lower():
                try:
                    # Open remote NetCDF via OPeNDAP
                    ds = xr.open_dataset(download_url)

                    # Extract data for the specified bounds
                    netcdf_data = self._extract_netcdf_data_from_dataset(ds, bounds, variable)
                    ds.close()

                    if netcdf_data:
                        print(f"         ✅ OPeNDAP NetCDF processing successful")
                        return netcdf_data

                except Exception as e:
                    print(f"         ⚠️ OPeNDAP failed: {e}")

            # Fallback: try direct download (if small enough)
            try:
                with tempfile.NamedTemporaryFile(suffix='.nc', delete=False) as tmp_file:
                    response = requests.get(download_url, headers=self.headers,
                                          stream=True, timeout=60)

                    if response.status_code == 200:
                        # Only download if file is reasonably small (< 100MB)
                        content_length = response.headers.get('content-length')
                        if content_length and int(content_length) > 100 * 1024 * 1024:
                            print(f"         ⚠️ File too large for direct download: {int(content_length)/(1024*1024*1024):.1f} GB")
                            print(f"         🔄 Using metadata-based analysis (this is normal for NASA data)")
                            return None

                        for chunk in response.iter_content(chunk_size=8192):
                            tmp_file.write(chunk)

                        tmp_file.flush()

                        # Process downloaded NetCDF file
                        ds = xr.open_dataset(tmp_file.name)
                        netcdf_data = self._extract_netcdf_data_from_dataset(ds, bounds, variable)
                        ds.close()

                        # Clean up
                        os.unlink(tmp_file.name)

                        if netcdf_data:
                            print(f"         ✅ Downloaded NetCDF processing successful")
                            return netcdf_data
                    else:
                        os.unlink(tmp_file.name)

            except Exception as e:
                print(f"         ⚠️ Download processing failed: {e}")

            return None

        except ImportError:
            print(f"         ⚠️ xarray not available for NetCDF processing")
            return None
        except Exception as e:
            print(f"         ❌ NetCDF granule processing error: {e}")
            return None

    def _extract_download_url(self, granule):
        """Extract download URL from granule metadata"""
        try:
            links = granule.get('links', [])

            for link in links:
                href = link.get('href', '')
                rel = link.get('rel', '')

                # Prefer OPeNDAP for remote access
                if 'opendap' in href.lower() or rel == 'opendap':
                    return href

                # Fallback to direct download
                if href.endswith('.nc') or 'download' in rel:
                    return href

            return None

        except Exception:
            return None

    def _extract_netcdf_data_from_dataset(self, ds, bounds, variable):
        """Extract data from xarray dataset"""
        try:
            # Determine variable names (varies by product)
            var_mapping = self._get_variable_mapping(ds, variable)
            if not var_mapping:
                return None

            lat_var = var_mapping['latitude']
            lon_var = var_mapping['longitude']
            data_var = var_mapping['data']
            quality_var = var_mapping.get('quality')

            # Get coordinate arrays
            lats = ds[lat_var].values
            lons = ds[lon_var].values

            # Create spatial mask for bounds
            lat_mask = (lats >= bounds[1]) & (lats <= bounds[3])
            lon_mask = (lons >= bounds[0]) & (lons <= bounds[2])

            # Extract data subset
            if len(lats.shape) == 1 and len(lons.shape) == 1:
                # 1D coordinate arrays
                data_subset = ds[data_var].sel(
                    {lat_var: lats[lat_mask], lon_var: lons[lon_mask]},
                    method='nearest'
                )
            else:
                # 2D coordinate arrays - more complex subsetting
                combined_mask = lat_mask & lon_mask
                data_subset = ds[data_var].where(combined_mask, drop=True)

            # Convert to numpy
            data_array = data_subset.values

            # Apply quality control if available
            if quality_var and quality_var in ds:
                quality_flags = ds[quality_var].where(combined_mask, drop=True).values
                data_array = self._apply_quality_control(data_array, quality_flags)

            # Create grid coordinates
            subset_lats = lats[lat_mask] if len(lats.shape) == 1 else lats[combined_mask]
            subset_lons = lons[lon_mask] if len(lons.shape) == 1 else lons[combined_mask]

            return {
                'data': data_array,
                'latitude': subset_lats,
                'longitude': subset_lons,
                'source': 'Experimental NASA NetCDF extraction',
                'processing_level': 'L3 NetCDF',
                'data_type': 'UNVALIDATED NASA NETCDF EXTRACT',
                'quality_controlled': quality_var is not None
            }

        except Exception as e:
            print(f"         ❌ NetCDF data extraction error: {e}")
            return None

    def _get_variable_mapping(self, ds, variable):
        """Get variable name mapping for different NASA products"""
        variables = list(ds.variables.keys())

        # Common patterns for different variables
        mappings = {
            'sst': {
                'data_patterns': ['sst', 'sea_surface_temperature', 'analysed_sst'],
                'lat_patterns': ['lat', 'latitude', 'nav_lat'],
                'lon_patterns': ['lon', 'longitude', 'nav_lon'],
                'quality_patterns': ['quality_level', 'l2p_flags', 'sst_dtime']
            },
            'chlorophyll': {
                'data_patterns': ['chlor_a', 'chl', 'chlorophyll_a'],
                'lat_patterns': ['lat', 'latitude'],
                'lon_patterns': ['lon', 'longitude'],
                'quality_patterns': ['l2_flags', 'qual_sst', 'flags']
            }
        }

        if variable not in mappings:
            return None

        patterns = mappings[variable]
        result = {}

        # Find data variable
        for pattern in patterns['data_patterns']:
            matches = [v for v in variables if pattern in v.lower()]
            if matches:
                result['data'] = matches[0]
                break

        # Find coordinate variables
        for pattern in patterns['lat_patterns']:
            matches = [v for v in variables if pattern in v.lower()]
            if matches:
                result['latitude'] = matches[0]
                break

        for pattern in patterns['lon_patterns']:
            matches = [v for v in variables if pattern in v.lower()]
            if matches:
                result['longitude'] = matches[0]
                break

        # Find quality variable (optional)
        for pattern in patterns['quality_patterns']:
            matches = [v for v in variables if pattern in v.lower()]
            if matches:
                result['quality'] = matches[0]
                break

        # Check if we have minimum required variables
        if 'data' in result and 'latitude' in result and 'longitude' in result:
            return result
        else:
            return None

    def _apply_quality_control(self, data, quality_flags):
        """Apply quality control using NASA quality flags"""
        try:
            if quality_flags is not None:
                # NASA quality flags: generally 0-1 = highest quality, 2-3 = good, 4+ = poor/invalid
                quality_mask = quality_flags <= 3  # Keep good to highest quality
                data_masked = np.where(quality_mask, data, np.nan)

                valid_percent = np.sum(quality_mask) / quality_mask.size * 100
                print(f"         📊 Quality control: {valid_percent:.1f}% data retained")

                return data_masked
            else:
                return data

        except Exception:
            return data

    def _convert_netcdf_to_grid(self, netcdf_data, bounds, grid_size):
        """Convert NetCDF data to expected grid format"""
        try:
            data_array = netcdf_data['data']
            lats = netcdf_data['latitude']
            lons = netcdf_data['longitude']

            # If data is already gridded, interpolate to desired grid size
            if len(data_array.shape) == 2:
                from scipy.interpolate import griddata

                # Create target grid
                lat_grid = np.linspace(bounds[1], bounds[3], grid_size)
                lon_grid = np.linspace(bounds[0], bounds[2], grid_size)
                lon_mesh, lat_mesh = np.meshgrid(lon_grid, lat_grid)

                # Flatten source coordinates and data
                if len(lats.shape) == 2:
                    lat_flat = lats.flatten()
                    lon_flat = lons.flatten()
                    data_flat = data_array.flatten()
                else:
                    # Create meshgrid from 1D coordinates
                    lon_src, lat_src = np.meshgrid(lons, lats)
                    lat_flat = lat_src.flatten()
                    lon_flat = lon_src.flatten()
                    data_flat = data_array.flatten()

                # Remove NaN values
                valid_mask = ~np.isnan(data_flat)
                if np.sum(valid_mask) > 10:  # Need at least 10 valid points
                    points = np.column_stack((lon_flat[valid_mask], lat_flat[valid_mask]))
                    values = data_flat[valid_mask]

                    # Interpolate to regular grid
                    grid_data = griddata(points, values, (lon_mesh, lat_mesh), method='linear')

                    print(f"         ✅ Interpolated NetCDF data to {grid_size}x{grid_size} grid")
                    return grid_data
                else:
                    print(f"         ⚠️ Insufficient valid data points for interpolation")

            # Fallback: create simple grid from available data
            grid_data = np.full((grid_size, grid_size), np.nan)
            if data_array.size > 0:
                mean_value = np.nanmean(data_array)
                if not np.isnan(mean_value):
                    # Fill grid with realistic variation around mean
                    noise = self.rng.normal(0, abs(mean_value) * 0.1, (grid_size, grid_size))
                    grid_data = mean_value + noise
                    print(f"         ✅ Created grid from NetCDF mean: {mean_value:.2f}")

            return grid_data

        except Exception as e:
            print(f"         ❌ NetCDF to grid conversion error: {e}")
            return None

    def _experimental_chlorophyll_grid(self, bounds, grid_size):
        """Attempt an experimental MODIS chlorophyll extraction."""
        print("      🔄 Downloading NASA MODIS Aqua Chlorophyll data...")

        try:
            # NASA CMR search for MODIS Aqua Chlorophyll
            params = {
                'collection_concept_id': 'C1996881226-POCLOUD',  # MODIS Aqua L3 CHL
                'temporal': '2024-01-01T00:00:00Z,2024-01-31T23:59:59Z',
                'bounding_box': f"{bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]}",
                'page_size': 10
            }

            response = requests.get(
                'https://cmr.earthdata.nasa.gov/search/granules.json',
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                granules = data.get('feed', {}).get('entry', [])

                if granules:
                    print(f"      ✅ Found {len(granules)} NASA Chlorophyll granules")

                    # Try enhanced NetCDF processing first
                    try:
                        import xarray as xr

                        # Process first few granules with full NetCDF if possible
                        for granule in granules[:3]:  # Try up to 3 granules
                            netcdf_data = self._process_netcdf_granule(granule, bounds, 'chlorophyll')
                            if netcdf_data:
                                print(f"      ✅ Enhanced NetCDF processing successful")
                                # Convert to expected grid format
                                return self._convert_netcdf_to_grid(netcdf_data, bounds, grid_size)

                        print(f"      ✅ Using NASA metadata approach (optimized for large datasets)")

                    except ImportError:
                        print(f"      ⚠️ xarray not available, using metadata approach")
                    except Exception as e:
                        print(f"      ⚠️ NetCDF processing error: {e}, using metadata approach")

                    # Fallback to metadata-based processing
                    return self._process_chl_granules(granules, bounds, grid_size)
                else:
                    print("      ❌ No NASA Chlorophyll granules found")
                    return None
            else:
                print(f"      ❌ NASA CMR error: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"      ❌ Chlorophyll download error: {e}")
            return None

    def _prepare_prototype_bathymetry_data(self, study_area):
        """Prepare an unvalidated prototype bathymetry layer."""
        print("      🔄 Generating deterministic prototype bathymetry...")
        return self._process_bathymetry_response(None, study_area['bounds'])

    def _build_prototype_environmental_data(self, study_area, bathymetry_data):
        """Build prototype environmental layers from available inputs."""
        
        bounds = study_area['bounds']  # [west, south, east, north]
        grid_size = 25  # High resolution
        
        # Create coordinate grids
        lats = np.linspace(bounds[1], bounds[3], grid_size)
        lons = np.linspace(bounds[0], bounds[2], grid_size)
        
        print("   🌡️ Generating deterministic SST prototype input...")
        sst_data = self._process_sst_granules([], bounds, grid_size)

        print("   🌱 Generating deterministic chlorophyll prototype input...")
        chl_data = self._process_chl_granules([], bounds, grid_size)

        return {
            'sst': {
                'data': sst_data,
                'latitudes': lats.tolist(),
                'longitudes': lons.tolist(),
                'source': 'Deterministic generated prototype',
                'accuracy': 'Not validated',
                'resolution': f'{grid_size}x{grid_size} demo grid',
                'algorithm': 'Latitude trend with seeded demo variation',
                'data_type': 'PROTOTYPE ENVIRONMENTAL GRID'
            },
            'chlorophyll': {
                'data': chl_data,
                'latitudes': lats.tolist(),
                'longitudes': lons.tolist(),
                'source': 'Deterministic generated prototype',
                'accuracy': 'Not validated',
                'resolution': f'{grid_size}x{grid_size} demo grid',
                'algorithm': 'Coastal-distance heuristic with seeded demo variation',
                'data_type': 'PROTOTYPE ENVIRONMENTAL GRID'
            },
            'bathymetry': {
                'data': bathymetry_data['depth_data'] if bathymetry_data else None,
                'source': 'Prototype bathymetry input',
                'accuracy': 'Not validated',
                'resolution': f'{grid_size}x{grid_size} demo grid',
                'algorithm': 'Generated depth heuristic',
                'quality': bathymetry_data.get('quality', 'Unvalidated') if bathymetry_data else 'No data'
            }
        }

    def _generate_bathymetry_data(self, study_area):
        """Generate realistic bathymetry data"""
        bounds = study_area['bounds']
        grid_size = 25

        lats = np.linspace(bounds[1], bounds[3], grid_size)
        lons = np.linspace(bounds[0], bounds[2], grid_size)

        depth_data = []
        for i, lat in enumerate(lats):
            depth_row = []
            for j, lon in enumerate(lons):
                # Distance from coast (simplified)
                coastal_distance = abs(lon + 122)  # California coast reference

                # Continental shelf model
                if coastal_distance < 0.5:  # Very close to coast
                    base_depth = -20 - (coastal_distance * 40)
                elif coastal_distance < 2.0:  # Continental shelf
                    base_depth = -50 - ((coastal_distance - 0.5) * 100)
                else:  # Deep ocean
                    base_depth = -200 - ((coastal_distance - 2.0) * 800)

                # Add seafloor topography
                seamount_effect = 150 * np.exp(-((lat - 36)**2 + (lon + 121)**2) / 4)
                canyon_effect = -200 * np.exp(-((lat - 35)**2 + (lon + 120)**2) / 2)
                ridge_effect = 100 * np.sin(lat * 0.2) * np.cos(lon * 0.15)

                # Combine effects
                depth = base_depth + seamount_effect + canyon_effect + ridge_effect
                depth = max(-4000, min(0, depth))  # Realistic depth range
                depth_row.append(depth)
            depth_data.append(depth_row)

        return {
            'depths': depth_data,
            'latitudes': lats.tolist(),
            'longitudes': lons.tolist(),
            'min_depth': np.min(depth_data),
            'max_depth': np.max(depth_data)
        }
    
    def advanced_habitat_prediction(self, environmental_data):
        """Calculate an unvalidated heuristic suitability score."""
        
        print("\n🧮 ADVANCED HABITAT SUITABILITY ANALYSIS")
        print("=" * 50)
        
        # Safely extract data arrays with error handling
        try:
            sst_data = np.array(environmental_data['sst']['data'])
            if sst_data.ndim == 0:  # 0-dimensional array
                sst_data = np.array([[sst_data.item()]])
            elif sst_data.ndim == 1:  # 1-dimensional array
                sst_data = sst_data.reshape(1, -1)
        except (KeyError, TypeError):
            print("⚠️ SST data issue, using default grid")
            sst_data = np.array([[20.0]])  # Default temperature

        try:
            chl_data = np.array(environmental_data['chlorophyll']['data'])
            if chl_data.ndim == 0:  # 0-dimensional array
                chl_data = np.array([[chl_data.item()]])
            elif chl_data.ndim == 1:  # 1-dimensional array
                chl_data = chl_data.reshape(1, -1)
        except (KeyError, TypeError):
            print("⚠️ Chlorophyll data issue, using default grid")
            chl_data = np.array([[1.0]])  # Default chlorophyll

        try:
            depth_data = np.array(environmental_data['bathymetry']['data'])
            if depth_data.ndim == 0:  # 0-dimensional array
                depth_data = np.array([[depth_data.item()]])
            elif depth_data.ndim == 1:  # 1-dimensional array
                depth_data = depth_data.reshape(1, -1)
        except (KeyError, TypeError):
            print("⚠️ Bathymetry data issue, using default grid")
            depth_data = np.array([[-100.0]])  # Default depth

        # Ensure all arrays have the same shape
        max_shape = max(sst_data.shape, chl_data.shape, depth_data.shape)
        if sst_data.shape != max_shape:
            sst_data = np.full(max_shape, sst_data.flat[0])
        if chl_data.shape != max_shape:
            chl_data = np.full(max_shape, chl_data.flat[0])
        if depth_data.shape != max_shape:
            depth_data = np.full(max_shape, depth_data.flat[0])

        grid_shape = sst_data.shape
        hsi_grid = np.zeros(grid_shape)
        uncertainty_grid = np.zeros(grid_shape)
        
        # Component grids
        temp_suitability = np.zeros(grid_shape)
        prod_suitability = np.zeros(grid_shape)
        front_suitability = np.zeros(grid_shape)
        depth_suitability = np.zeros(grid_shape)
        
        for i in range(grid_shape[0]):
            for j in range(grid_shape[1]):
                try:
                    sst = sst_data[i, j] if i < sst_data.shape[0] and j < sst_data.shape[1] else sst_data.flat[0]
                    chl = chl_data[i, j] if i < chl_data.shape[0] and j < chl_data.shape[1] else chl_data.flat[0]
                    depth = depth_data[i, j] if i < depth_data.shape[0] and j < depth_data.shape[1] else depth_data.flat[0]
                except IndexError:
                    # Fallback to first available value
                    sst = sst_data.flat[0] if sst_data.size > 0 else 20.0
                    chl = chl_data.flat[0] if chl_data.size > 0 else 1.0
                    depth = depth_data.flat[0] if depth_data.size > 0 else -100.0

                # 1. Bioenergetic Temperature Suitability (Sharpe-Schoolfield)
                temp_suit, temp_unc = self._bioenergetic_temperature_model(sst)
                temp_suitability[i, j] = temp_suit

                # 2. Trophic Productivity Suitability (Eppley + Transfer)
                prod_suit, prod_unc = self._trophic_productivity_model(chl, sst)
                prod_suitability[i, j] = prod_suit

                # 3. Frontal Zone Suitability (Gradient-based)
                front_suit, front_unc = self._frontal_zone_model(i, j, sst_data, chl_data)
                front_suitability[i, j] = front_suit

                # 4. Depth Suitability (Species-specific)
                depth_suit, depth_unc = self._depth_suitability_model(depth)
                depth_suitability[i, j] = depth_suit

                # 5. Ecological Factors
                prey_availability = self._calculate_prey_availability(sst, chl, depth)
                predator_effects = self._calculate_predator_effects(i, j)
                human_impact = self._calculate_human_impacts(i, j)
                temporal_effects = self._calculate_temporal_effects()

                # 6. Additional prototype response factors
                # Calculate coordinates (simplified grid mapping)
                lat = 32 + (i / grid_shape[0]) * 10  # 32-42°N
                lon = -125 + (j / grid_shape[1]) * 10  # -125 to -115°W

                # Ocean dynamics effects
                current_effects = self._calculate_ocean_current_effects(lat, lon, depth)
                upwelling_effects = self._calculate_upwelling_effects(lat, lon)
                eddy_effects = self._calculate_mesoscale_eddy_effects(lat, lon)

                # Water quality effects
                oxygen_effects = self._calculate_dissolved_oxygen_effects(depth, sst)
                salinity_effects = self._calculate_salinity_effects(lat, lon)
                ph_effects = self._calculate_ph_effects(depth)
                turbidity_effects = self._calculate_turbidity_effects(lat, lon, chl)

                # Weather and storm effects
                storm_effects = self._calculate_storm_effects(lat, lon)
                wind_mixing_effects = self._calculate_wind_mixing_effects(depth)

                # 6. Enhanced Weighted Integration
                # Adjust weights based on species and conditions
                weights = self._calculate_adaptive_weights(temp_suit, prod_suit, front_suit, depth_suit)
                
                # Avoid zero values in geometric mean
                temp_suit = max(temp_suit, 0.001)
                prod_suit = max(prod_suit, 0.001)
                front_suit = max(front_suit, 0.001)
                depth_suit = max(depth_suit, 0.001)

                # Calculate HSI with synergistic effects
                base_hsi = (temp_suit**weights[0] * prod_suit**weights[1] *
                           front_suit**weights[2] * depth_suit**weights[3])

                # Apply synergistic interactions
                synergy_multiplier = self._calculate_synergistic_effects(
                    temp_suit, prod_suit, front_suit, depth_suit,
                    sst, chl, depth
                )

                # Apply ecological and human factors
                ecological_multiplier = (prey_availability * 0.4 +
                                       predator_effects * 0.3 +
                                       (1 - human_impact) * 0.2 +
                                       temporal_effects * 0.1)

                # Combine the additional heuristic response factors.
                ocean_dynamics_multiplier = (current_effects * 0.4 +
                                           upwelling_effects * 0.3 +
                                           eddy_effects * 0.3)

                water_quality_multiplier = (oxygen_effects * 0.4 +
                                          salinity_effects * 0.3 +
                                          ph_effects * 0.2 +
                                          turbidity_effects * 0.1)

                weather_multiplier = (storm_effects * 0.6 +
                                    wind_mixing_effects * 0.4)

                # Final heuristic suitability calculation.
                hsi = (base_hsi *
                      synergy_multiplier *
                      ecological_multiplier *
                      ocean_dynamics_multiplier *
                      water_quality_multiplier *
                      weather_multiplier)

                hsi_grid[i, j] = hsi

                # Combined uncertainty
                combined_uncertainty = np.sqrt(
                    (weights[0] * temp_unc)**2 +
                    (weights[1] * prod_unc)**2 +
                    (weights[2] * front_unc)**2 +
                    (weights[3] * depth_unc)**2
                )
                uncertainty_grid[i, j] = combined_uncertainty
        
        return {
            'hsi': hsi_grid.tolist(),
            'uncertainty': uncertainty_grid.tolist(),
            'components': {
                'temperature': temp_suitability.tolist(),
                'productivity': prod_suitability.tolist(),
                'frontal': front_suitability.tolist(),
                'depth': depth_suitability.tolist()
            },
            'statistics': self._calculate_statistics(hsi_grid, uncertainty_grid),
            'environmental_data': environmental_data
        }
    
    def _bioenergetic_temperature_model(self, temp):
        """Sharpe-Schoolfield bioenergetic temperature model"""
        params = self.shark_params
        
        if temp < params['temp_range'][0] or temp > params['temp_range'][1]:
            return 0.0, 0.5
        
        # Arrhenius component
        arrhenius = np.exp(params['thermal_coeff'] * (temp - params['optimal_temp']) / 10)
        
        # High temperature inactivation
        if temp > params['optimal_temp']:
            inactivation = 1 / (1 + np.exp(0.5 * (temp - params['temp_range'][1])))
        else:
            inactivation = 1.0
        
        # Low temperature limitation
        if temp < params['optimal_temp']:
            limitation = 1 / (1 + np.exp(-2 * (temp - params['temp_range'][0])))
        else:
            limitation = 1.0
        
        suitability = arrhenius * inactivation * limitation
        suitability = min(1.0, max(0.0, suitability))
        
        # Uncertainty increases away from optimal
        temp_deviation = abs(temp - params['optimal_temp']) / params['temp_tolerance']
        uncertainty = 0.1 + 0.3 * temp_deviation
        
        return suitability, uncertainty
    
    def _trophic_productivity_model(self, chl, sst):
        """Eppley + Trophic Transfer + Michaelis-Menten model"""
        params = self.shark_params
        
        # Primary productivity (Eppley 1972)
        temp_factor = np.exp(0.0633 * sst)
        primary_productivity = chl * temp_factor
        
        # Trophic transfer (Lindeman 1942)
        transfer_efficiency = 0.1  # 10% rule
        available_energy = primary_productivity * (transfer_efficiency ** (params['trophic_level'] - 1))
        
        # Michaelis-Menten response
        energy_suitability = available_energy / (available_energy + params['productivity_threshold'])
        
        # Prey aggregation effect
        aggregation_factor = 1 + 0.5 * np.tanh(chl - 0.5)
        
        suitability = energy_suitability * aggregation_factor
        suitability = min(1.0, max(0.0, suitability))
        
        # Uncertainty
        uncertainty = 0.3 * (1 - suitability)
        
        return suitability, uncertainty
    
    def _frontal_zone_model(self, i, j, sst_data, chl_data):
        """Advanced frontal zone model with multi-scale detection and temporal persistence"""
        params = self.shark_params

        # Multi-scale gradient analysis
        gradients = self._calculate_multiscale_gradients(i, j, sst_data, chl_data)

        # Canny edge detection for front boundaries
        front_edges = self._canny_front_detection(gradients)

        # Temporal persistence (simplified for now)
        persistence_score = 0.5  # Moderate persistence assumption

        # Front strength classification
        front_strength = self._classify_front_strength(gradients, front_edges)

        # Species-specific frontal affinity with enhancements
        enhanced_affinity = params['frontal_affinity'] * (1 + persistence_score * 0.3)

        # Combined suitability with prey aggregation
        prey_aggregation = 1 + 2 * front_strength
        suitability = enhanced_affinity * front_strength * prey_aggregation
        suitability = min(1.0, max(0.0, suitability))

        # Advanced uncertainty calculation
        uncertainty = self._calculate_frontal_uncertainty(gradients, persistence_score, front_strength)

        return suitability, uncertainty

    def _depth_suitability_model(self, depth):
        """Advanced depth model with diel migration, thermocline, and oxygen effects"""
        params = self.shark_params

        # Convert depth to positive value (depth is negative)
        depth_positive = abs(depth)

        # Base depth preference
        base_suitability = self._base_depth_preference(depth_positive, params)

        # Diel vertical migration effect
        current_hour = 12  # Simplified - assume noon for now
        diel_effect = self._diel_migration_effect(depth_positive, current_hour, params)

        # Thermocline effect
        thermocline_effect = self._thermocline_effect(depth_positive, params)

        # Oxygen minimum zone effect
        oxygen_effect = self._oxygen_minimum_zone_effect(depth_positive)

        # Pressure tolerance effect
        pressure_effect = self._pressure_tolerance_effect(depth_positive, params)

        # Combined suitability with weighted factors
        total_suitability = (base_suitability * 0.4 +
                           diel_effect * 0.2 +
                           thermocline_effect * 0.2 +
                           oxygen_effect * 0.1 +
                           pressure_effect * 0.1)

        suitability = min(1.0, max(0.0, total_suitability))

        # Advanced uncertainty calculation
        uncertainty = self._calculate_depth_uncertainty(depth_positive, params, base_suitability)

        return suitability, uncertainty

    def _base_depth_preference(self, depth_positive, params):
        """Basic species-specific depth preference"""
        min_depth, max_depth = params['depth_preference']

        if min_depth <= depth_positive <= max_depth:
            # Within preferred range - Gaussian response
            optimal_depth = (min_depth + max_depth) / 2
            depth_deviation = abs(depth_positive - optimal_depth) / (max_depth - min_depth)
            return np.exp(-2 * depth_deviation**2)
        else:
            # Outside preferred range - exponential decay
            if depth_positive < min_depth:
                return np.exp(-(min_depth - depth_positive) / 50)
            else:
                return np.exp(-(depth_positive - max_depth) / 100)

    def _diel_migration_effect(self, depth_positive, hour, params):
        """Diel vertical migration patterns"""
        # Migration amplitude varies by species
        migration_amplitude = params.get('diel_migration', 50)  # meters

        # Most sharks: deeper during day, shallower at night
        if params.get('diel_pattern', 'normal') == 'normal':
            # Sinusoidal pattern: deeper at noon (12), shallower at midnight (0/24)
            depth_adjustment = migration_amplitude * np.sin(2 * np.pi * (hour - 6) / 24)
        else:
            # Reverse pattern for some species
            depth_adjustment = -migration_amplitude * np.sin(2 * np.pi * (hour - 6) / 24)

        # Calculate optimal depth for current time
        base_optimal = sum(params['depth_preference']) / 2
        time_optimal_depth = base_optimal + depth_adjustment

        # Suitability based on how close current depth is to time-optimal depth
        depth_difference = abs(depth_positive - time_optimal_depth)

        if depth_difference < 20:  # Within normal migration range
            return 1.0
        else:
            return np.exp(-depth_difference / 40)

    def _thermocline_effect(self, depth_positive, params):
        """Thermocline interaction effects"""
        thermocline_depth = 100  # meters (typical)
        thermocline_strength = 5  # °C difference

        # Temperature effect based on depth relative to thermocline
        if depth_positive < thermocline_depth:
            # Above thermocline - warmer water
            temp_effect = 1.0
        else:
            # Below thermocline - cooler water
            temp_drop = thermocline_strength * (depth_positive - thermocline_depth) / 100
            temp_effect = np.exp(-temp_drop / params.get('temp_tolerance', 3))

        # Some species prefer thermocline boundaries (feeding opportunities)
        thermocline_proximity = abs(depth_positive - thermocline_depth)
        if thermocline_proximity < 20:  # Near thermocline
            boundary_bonus = 1.2 * params.get('thermocline_affinity', 0.5)
        else:
            boundary_bonus = 1.0

        return temp_effect * boundary_bonus

    def _oxygen_minimum_zone_effect(self, depth_positive):
        """Oxygen minimum zone (typically 200-1000m in many oceans)"""
        omz_start = 200
        omz_end = 1000

        if omz_start <= depth_positive <= omz_end:
            # Reduced suitability in oxygen minimum zone
            # Sinusoidal reduction with minimum at mid-depth
            omz_position = (depth_positive - omz_start) / (omz_end - omz_start)
            omz_intensity = 1 - 0.5 * np.sin(np.pi * omz_position)
            return omz_intensity
        else:
            return 1.0

    def _pressure_tolerance_effect(self, depth_positive, params):
        """Pressure tolerance limits"""
        max_depth_tolerance = params.get('max_depth_tolerance', 1000)

        if depth_positive > max_depth_tolerance:
            # Exponential decay beyond maximum tolerance
            excess_depth = depth_positive - max_depth_tolerance
            return np.exp(-excess_depth / 200)
        else:
            return 1.0

    def _calculate_depth_uncertainty(self, depth_positive, params, base_suitability):
        """Advanced uncertainty calculation for depth model"""
        min_depth, max_depth = params['depth_preference']

        # Base uncertainty
        base_uncertainty = 0.1

        # Increase uncertainty at depth extremes
        if depth_positive < min_depth or depth_positive > max_depth:
            extreme_penalty = 0.3
        else:
            extreme_penalty = 0.0

        # Increase uncertainty for low suitability areas
        suitability_penalty = (1 - base_suitability) * 0.2

        # Species-specific uncertainty
        if params['habitat_specificity'] == 'open_ocean':
            # Pelagic species have higher depth uncertainty
            species_penalty = 0.1
        else:
            species_penalty = 0.0

        total_uncertainty = base_uncertainty + extreme_penalty + suitability_penalty + species_penalty

        return max(0.05, min(0.5, total_uncertainty))

    def _calculate_synergistic_effects(self, temp_suit, prod_suit, front_suit, depth_suit, sst, chl, depth):
        """Calculate synergistic interactions between environmental factors"""
        params = self.shark_params

        # Temperature-Productivity synergy
        temp_prod_synergy = self._temperature_productivity_synergy(temp_suit, prod_suit, sst, chl, params)

        # Frontal-Depth synergy
        front_depth_synergy = self._frontal_depth_synergy(front_suit, depth_suit, depth, params)

        # Temperature-Depth synergy (thermoregulation)
        temp_depth_synergy = self._temperature_depth_synergy(temp_suit, depth_suit, sst, depth, params)

        # Productivity-Frontal synergy (enhanced feeding)
        prod_front_synergy = self._productivity_frontal_synergy(prod_suit, front_suit, chl, params)

        # Combined synergy multiplier
        total_synergy = (temp_prod_synergy * 0.3 +
                        front_depth_synergy * 0.25 +
                        temp_depth_synergy * 0.25 +
                        prod_front_synergy * 0.2)

        # Synergy multiplier (1.0 = no effect, >1.0 = positive synergy, <1.0 = negative)
        synergy_multiplier = 1.0 + total_synergy

        return max(0.5, min(1.5, synergy_multiplier))  # Limit synergy effects

    def _temperature_productivity_synergy(self, temp_suit, prod_suit, sst, chl, params):
        """Synergy between temperature and productivity"""
        # Optimal temperature enhances productivity utilization
        if temp_suit > 0.8 and prod_suit > 0.6:
            # High temperature + high productivity = super optimal conditions
            synergy = 0.3 * temp_suit * prod_suit
        elif temp_suit < 0.3 and prod_suit > 0.8:
            # Cold water but high productivity = reduced benefit
            synergy = -0.2 * (1 - temp_suit) * prod_suit
        elif temp_suit > 0.7 and prod_suit < 0.3:
            # Good temperature but low productivity = metabolic stress
            synergy = -0.15 * temp_suit * (1 - prod_suit)
        else:
            synergy = 0.0

        return synergy

    def _frontal_depth_synergy(self, front_suit, depth_suit, depth, params):
        """Synergy between frontal zones and depth"""
        # Fronts often extend vertically - depth matters for front utilization
        if front_suit > 0.7 and depth_suit > 0.6:
            # Strong front + good depth = enhanced feeding opportunity
            depth_positive = abs(depth)

            # Fronts are most productive in upper water column
            if depth_positive < 100:
                depth_bonus = 1.0
            elif depth_positive < 200:
                depth_bonus = 0.7
            else:
                depth_bonus = 0.4

            synergy = 0.25 * front_suit * depth_suit * depth_bonus
        else:
            synergy = 0.0

        return synergy

    def _temperature_depth_synergy(self, temp_suit, depth_suit, sst, depth, params):
        """Synergy between temperature and depth preferences (thermoregulation)"""
        # Some species use depth to thermoregulate
        thermoregulation_ability = params.get('thermoregulation', 0.5)
        depth_positive = abs(depth)

        # Poor surface temperature but good depth access = thermoregulation benefit
        if temp_suit < 0.5 and depth_suit > 0.7 and depth_positive > 50:
            # Can dive to find better temperatures
            synergy = thermoregulation_ability * (1 - temp_suit) * depth_suit * 0.2
        elif temp_suit > 0.8 and depth_suit > 0.8:
            # Preferred temperature and depth yield the strongest heuristic interaction.
            synergy = 0.15 * temp_suit * depth_suit
        else:
            synergy = 0.0

        return synergy

    def _productivity_frontal_synergy(self, prod_suit, front_suit, chl, params):
        """Synergy between productivity and frontal zones (enhanced feeding)"""
        # High productivity + strong fronts = concentrated prey
        if prod_suit > 0.6 and front_suit > 0.6:
            # Both high = super feeding conditions
            feeding_efficiency = params.get('feeding_efficiency', 0.7)
            synergy = 0.2 * prod_suit * front_suit * feeding_efficiency
        elif prod_suit < 0.3 and front_suit > 0.8:
            # Low productivity but strong front = front may not be productive
            synergy = -0.1 * (1 - prod_suit) * front_suit
        else:
            synergy = 0.0

        return synergy

    def _calculate_prey_availability(self, sst, chl, depth):
        """Calculate prey availability based on environmental conditions"""
        params = self.shark_params
        prey_preferences = params.get('prey_preferences', ['small_fish'])

        total_prey_availability = 0
        for prey_type in prey_preferences:
            if prey_type in self.prey_models:
                prey_model = self.prey_models[prey_type]

                # Temperature suitability for prey
                prey_temp_suit = self._calculate_prey_temperature_suitability(sst, prey_model)

                # Depth suitability for prey
                prey_depth_suit = self._calculate_prey_depth_suitability(abs(depth), prey_model)

                # Productivity effect on prey
                prey_prod_effect = min(1.0, chl / 0.5)  # Normalized to typical chl values

                # Combined prey availability
                prey_availability = prey_temp_suit * prey_depth_suit * prey_prod_effect

                # Seasonal adjustment
                season = 'summer'  # Simplified - would use actual date
                seasonal_factor = prey_model.get('seasonal_abundance', {}).get(season, 1.0)

                total_prey_availability += prey_availability * seasonal_factor

        # Normalize by number of prey types
        if len(prey_preferences) > 0:
            total_prey_availability /= len(prey_preferences)

        return min(1.0, max(0.0, total_prey_availability))

    def _calculate_prey_temperature_suitability(self, sst, prey_model):
        """Calculate temperature suitability for prey species"""
        optimal_temp = prey_model['optimal_temp']
        temp_range = prey_model['temp_range']

        if temp_range[0] <= sst <= temp_range[1]:
            # Within range - Gaussian response
            deviation = abs(sst - optimal_temp) / (temp_range[1] - temp_range[0])
            return np.exp(-2 * deviation**2)
        else:
            # Outside range
            return 0.1

    def _calculate_prey_depth_suitability(self, depth_positive, prey_model):
        """Calculate depth suitability for prey species"""
        depth_pref = prey_model['depth_preference']

        if depth_pref[0] <= depth_positive <= depth_pref[1]:
            return 1.0
        else:
            # Exponential decay outside preferred range
            if depth_positive < depth_pref[0]:
                return np.exp(-(depth_pref[0] - depth_positive) / 20)
            else:
                return np.exp(-(depth_positive - depth_pref[1]) / 50)

    def _calculate_predator_effects(self, i, j):
        """Calculate predator-predator interaction effects"""
        # Simplified - in full implementation would track other shark densities

        # Killer whale avoidance
        orca_avoidance = self.predator_interactions['killer_whale_avoidance'][self.current_species]
        orca_presence_prob = 0.1  # Simplified - 10% chance of orca presence
        orca_effect = 1 - (orca_presence_prob * orca_avoidance)

        # Competitive exclusion (simplified)
        competition_effect = 0.9  # Assume 10% reduction due to competition

        # Size-based dominance
        size_dominance = 1.0  # Assume adult sharks

        total_predator_effect = orca_effect * competition_effect * size_dominance

        return max(0.1, min(1.0, total_predator_effect))

    def _calculate_human_impacts(self, i, j):
        """Calculate human impact effects"""
        # Simplified - in full implementation would use real fishing/shipping data

        # Fishing pressure (distance from coast proxy)
        coastal_distance = 0.5  # Simplified - assume moderate distance
        fishing_impact = coastal_distance * 0.3  # Closer to coast = more fishing

        # Marine traffic
        traffic_impact = 0.1  # Low traffic assumption

        # Pollution
        pollution_impact = 0.05  # Low pollution assumption

        total_human_impact = fishing_impact + traffic_impact + pollution_impact

        return max(0.0, min(0.8, total_human_impact))  # Cap at 80% impact

    def _calculate_temporal_effects(self):
        """Calculate temporal factor effects"""
        # Simplified - would use actual date/time in full implementation

        # Lunar cycle effect
        moon_phase = 'full_moon'  # Simplified
        lunar_effect = self.temporal_factors['lunar_cycles'][moon_phase]['feeding_activity']

        # Tidal effect
        tidal_effect = self.temporal_factors['tidal_effects']['high_tide']['feeding_opportunity']

        # Seasonal behavior
        seasonal_effect = 1.0  # Neutral season

        # Combined temporal effect
        total_temporal = (lunar_effect * 0.4 + tidal_effect * 0.4 + seasonal_effect * 0.2) / 3

        return max(0.5, min(1.5, total_temporal))

    def _calculate_adaptive_weights(self, temp_suit, prod_suit, front_suit, depth_suit):
        """Calculate adaptive weights based on species and conditions"""
        params = self.shark_params

        # Base weights
        base_weights = [0.3, 0.25, 0.2, 0.25]  # temp, productivity, frontal, depth

        # Species-specific weight adjustments
        if params['habitat_specificity'] == 'pelagic_oceanic':
            # Pelagic species: less weight on coastal factors, more on temperature
            weights = [0.35, 0.3, 0.15, 0.2]
        elif params['habitat_specificity'] == 'estuarine_coastal':
            # Coastal species: more weight on depth and frontal zones
            weights = [0.25, 0.2, 0.3, 0.25]
        elif params['habitat_specificity'] == 'tropical_pelagic':
            # Tropical pelagic: balanced but emphasize productivity
            weights = [0.3, 0.3, 0.2, 0.2]
        else:
            weights = base_weights

        # Condition-based adjustments
        if temp_suit < 0.3:
            # Poor temperature - increase temperature weight
            weights[0] *= 1.2
            # Normalize
            total = sum(weights)
            weights = [w/total for w in weights]

        return weights

    def _calculate_ocean_current_effects(self, lat, lon, depth):
        """Calculate ocean current effects on habitat suitability"""
        # Determine current system based on location
        if -130 < lon < -110 and 30 < lat < 45:
            # California Current system
            current_system = self.ocean_dynamics['current_systems']['california_current']
        elif -85 < lon < -70 and 25 < lat < 45:
            # Gulf Stream system
            current_system = self.ocean_dynamics['current_systems']['gulf_stream']
        else:
            # Default weak current
            return 0.9

        # Calculate current strength at depth
        depth_positive = abs(depth)
        if current_system['depth_profile'] == 'exponential_decay':
            depth_factor = np.exp(-depth_positive / 100)
        else:  # linear_decay
            depth_factor = max(0.1, 1 - depth_positive / 200)

        # Current velocity magnitude
        u_vel = current_system['velocity_u']
        v_vel = current_system['velocity_v']
        current_speed = np.sqrt(u_vel**2 + v_vel**2) * depth_factor

        # Species-specific current preferences
        params = self.shark_params
        if params.get('habitat_specificity') == 'pelagic_oceanic':
            # Pelagic species benefit from moderate currents (prey transport)
            if 0.2 < current_speed < 0.8:
                current_effect = 1.2
            else:
                current_effect = 1.0
        else:
            # Coastal species prefer weaker currents
            if current_speed < 0.3:
                current_effect = 1.1
            else:
                current_effect = 0.9

        return max(0.5, min(1.5, current_effect))

    def _calculate_upwelling_effects(self, lat, lon):
        """Calculate upwelling effects on habitat suitability"""
        # Check if in major upwelling zone
        upwelling_effect = 1.0

        if -130 < lon < -115 and 30 < lat < 45:
            # California upwelling
            upwelling_zone = self.ocean_dynamics['upwelling_zones']['california_coast']
            # Summer peak upwelling (simplified)
            seasonal_factor = 1.0  # Would use actual date
            upwelling_strength = upwelling_zone['strength'] * seasonal_factor

            # Enhanced productivity from upwelling
            productivity_boost = upwelling_zone['nutrient_enhancement']
            temperature_effect = upwelling_zone['temperature_depression']

            # Species-specific responses to upwelling
            params = self.shark_params
            if params.get('habitat_specificity') in ['temperate_coastal', 'pelagic_oceanic']:
                # Cold-water species benefit from upwelling
                upwelling_effect = 1.0 + (upwelling_strength * 0.3)
            else:
                # Warm-water species less favorable
                upwelling_effect = 1.0 - (upwelling_strength * 0.1)

        return max(0.7, min(1.4, upwelling_effect))

    def _calculate_mesoscale_eddy_effects(self, lat, lon):
        """Calculate mesoscale eddy effects"""
        # Simplified eddy detection (would use real eddy tracking data)
        eddy_probability = 0.15  # 15% chance of eddy presence

        if self.rng.random() < eddy_probability:
            # Determine eddy type
            if self.rng.random() < 0.6:
                # Cold-core eddy (more common)
                eddy_type = self.ocean_dynamics['mesoscale_eddies']['cold_core_eddies']
                temp_anomaly = eddy_type['temperature_anomaly']  # -1.5°C
                productivity_effect = eddy_type['productivity_effect']  # +0.5
            else:
                # Warm-core eddy
                eddy_type = self.ocean_dynamics['mesoscale_eddies']['warm_core_eddies']
                temp_anomaly = eddy_type['temperature_anomaly']  # +2.0°C
                productivity_effect = eddy_type['productivity_effect']  # -0.3

            # Species response to eddy conditions
            params = self.shark_params
            optimal_temp = params['optimal_temp']

            # Temperature effect
            if temp_anomaly > 0:  # Warm eddy
                if optimal_temp > 22:  # Warm-water species
                    temp_effect = 1.2
                else:  # Cold-water species
                    temp_effect = 0.8
            else:  # Cold eddy
                if optimal_temp < 20:  # Cold-water species
                    temp_effect = 1.2
                else:  # Warm-water species
                    temp_effect = 0.8

            # Productivity effect
            prod_effect = 1.0 + productivity_effect

            # Combined eddy effect
            eddy_effect = (temp_effect * 0.6 + prod_effect * 0.4)
        else:
            eddy_effect = 1.0

        return max(0.6, min(1.4, eddy_effect))

    def _calculate_dissolved_oxygen_effects(self, depth, sst):
        """Calculate dissolved oxygen effects"""
        depth_positive = abs(depth)
        oxygen_params = self.water_quality['dissolved_oxygen']

        # Calculate oxygen concentration at depth
        if depth_positive < 50:
            # Surface layer - high oxygen
            oxygen_conc = oxygen_params['surface_concentration']
        elif 50 <= depth_positive < 200:
            # Thermocline - reduced oxygen
            reduction_factor = oxygen_params['thermocline_reduction']
            oxygen_conc = oxygen_params['surface_concentration'] * (1 - reduction_factor)
        elif oxygen_params['omz_depth_range'][0] <= depth_positive <= oxygen_params['omz_depth_range'][1]:
            # Oxygen minimum zone
            oxygen_conc = oxygen_params['omz_concentration']
        else:
            # Deep water - moderate oxygen
            oxygen_conc = oxygen_params['surface_concentration'] * 0.7

        # Temperature effect on oxygen solubility
        temp_effect = np.exp(-0.02 * (sst - 15))  # Oxygen decreases with temperature
        oxygen_conc *= temp_effect

        # Species-specific oxygen tolerance
        species_tolerance = oxygen_params['species_tolerance'].get(self.current_species,
                                                                 {'min_oxygen': 4.0, 'optimal': 6.0})

        min_oxygen = species_tolerance['min_oxygen']
        optimal_oxygen = species_tolerance['optimal']

        if oxygen_conc < min_oxygen:
            # Below minimum tolerance
            oxygen_effect = 0.1
        elif oxygen_conc < optimal_oxygen:
            # Below optimal but tolerable
            oxygen_effect = 0.5 + 0.5 * (oxygen_conc - min_oxygen) / (optimal_oxygen - min_oxygen)
        else:
            # At or above optimal
            oxygen_effect = 1.0

        return max(0.1, min(1.0, oxygen_effect))

    def _calculate_salinity_effects(self, lat, lon):
        """Calculate salinity effects on habitat suitability"""
        salinity_params = self.water_quality['salinity']

        # Estimate salinity based on location
        if abs(lat) < 30:  # Tropical - higher evaporation
            base_salinity = salinity_params['open_ocean'] + 1.0
        elif abs(lat) > 60:  # Polar - lower salinity
            base_salinity = salinity_params['open_ocean'] - 2.0
        else:
            base_salinity = salinity_params['open_ocean']

        # Coastal influence (simplified)
        coastal_distance = min(abs(lon + 120), abs(lon + 80))  # Distance from major coasts
        if coastal_distance < 5:  # Near coast
            salinity = base_salinity - salinity_params['coastal_variation']
        else:
            salinity = base_salinity

        # Species-specific salinity tolerance
        species_tolerance = salinity_params['species_tolerance'].get(self.current_species)
        if not species_tolerance:
            return 1.0  # No specific requirements

        min_sal = species_tolerance['min_salinity']
        max_sal = species_tolerance['max_salinity']
        optimal_sal = species_tolerance['optimal']

        if min_sal <= salinity <= max_sal:
            # Within tolerance range
            deviation = abs(salinity - optimal_sal) / (max_sal - min_sal)
            salinity_effect = np.exp(-2 * deviation**2)
        else:
            # Outside tolerance
            salinity_effect = 0.1

        return max(0.1, min(1.0, salinity_effect))

    def _calculate_ph_effects(self, depth):
        """Calculate pH effects on habitat suitability"""
        ph_params = self.water_quality['ph_levels']
        depth_positive = abs(depth)

        # pH decreases with depth
        if depth_positive < 100:
            ph_level = ph_params['surface_ph']
        else:
            # Linear decrease with depth
            ph_decrease = (depth_positive - 100) / 1000 * (ph_params['surface_ph'] - ph_params['deep_water_ph'])
            ph_level = ph_params['surface_ph'] - ph_decrease

        # Ocean acidification effect (simplified)
        years_since_baseline = 10  # Assume 10 years of acidification
        acidification_effect = ph_params['acidification_trend'] * years_since_baseline
        ph_level += acidification_effect

        # Species-specific pH sensitivity
        species_sensitivity = ph_params['species_sensitivity'].get(self.current_species)
        if not species_sensitivity:
            return 1.0  # No specific sensitivity

        min_ph = species_sensitivity['min_ph']
        optimal_ph = species_sensitivity['optimal']

        if ph_level >= optimal_ph:
            ph_effect = 1.0
        elif ph_level >= min_ph:
            ph_effect = 0.5 + 0.5 * (ph_level - min_ph) / (optimal_ph - min_ph)
        else:
            ph_effect = 0.2  # Severe stress

        return max(0.2, min(1.0, ph_effect))

    def _calculate_turbidity_effects(self, lat, lon, chl):
        """Calculate turbidity effects on hunting efficiency"""
        turbidity_params = self.water_quality['turbidity']

        # Estimate turbidity from chlorophyll and location
        base_turbidity = turbidity_params['clear_water']

        # Coastal areas have higher turbidity
        coastal_distance = min(abs(lon + 120), abs(lon + 80))
        if coastal_distance < 2:
            base_turbidity = turbidity_params['coastal_turbidity']
        elif coastal_distance < 10:
            base_turbidity = turbidity_params['clear_water'] * 3

        # High chlorophyll increases turbidity
        chl_turbidity = chl * 2  # Simplified relationship
        total_turbidity = base_turbidity + chl_turbidity

        # Species-specific turbidity effects
        params = self.shark_params
        hunting_strategy = params.get('hunting_strategy', 'generalist_predator')

        if hunting_strategy in ['ambush_predator', 'high_speed_predator']:
            # Visual predators affected by turbidity
            hunting_params = turbidity_params['hunting_efficiency']['visual_predators']
            optimal_turbidity = hunting_params['optimal_turbidity']
            max_turbidity = hunting_params['max_turbidity']

            if total_turbidity <= optimal_turbidity:
                turbidity_effect = 1.0
            elif total_turbidity <= max_turbidity:
                turbidity_effect = 1.0 - 0.5 * (total_turbidity - optimal_turbidity) / (max_turbidity - optimal_turbidity)
            else:
                turbidity_effect = 0.3  # Severely impaired hunting
        else:
            # Electroreception-based hunters less affected
            independence = turbidity_params['hunting_efficiency']['electroreception']['turbidity_independence']
            turbidity_effect = independence + (1 - independence) * np.exp(-total_turbidity / 10)

        return max(0.3, min(1.0, turbidity_effect))

    def _calculate_storm_effects(self, lat, lon):
        """Calculate storm and weather effects"""
        storm_params = self.weather_effects['storm_systems']

        # Simplified storm probability based on location and season
        if 10 < abs(lat) < 40:  # Hurricane/typhoon belt
            storm_probability = 0.1  # 10% chance of storm influence
        else:
            storm_probability = 0.05

        if self.rng.random() < storm_probability:
            # Storm present - determine category (simplified)
            storm_category = self.rng.choice(['cat_1', 'cat_2', 'cat_3'], p=[0.5, 0.3, 0.2])
            storm_data = storm_params['hurricane_categories'][storm_category]

            # Species-specific storm response
            species_response = storm_params['species_responses'].get(self.current_species,
                                                                   {'storm_avoidance': 0.5, 'deep_refuge': 0.5})

            # Storm displacement effect
            avoidance_factor = species_response['storm_avoidance']
            storm_effect = 1.0 - (avoidance_factor * 0.6)  # Reduced habitat suitability
        else:
            storm_effect = 1.0

        return max(0.4, min(1.0, storm_effect))

    def _calculate_wind_mixing_effects(self, depth):
        """Calculate wind-driven mixing effects"""
        wind_params = self.weather_effects['wind_effects']
        depth_positive = abs(depth)

        # Simplified wind speed (would use real weather data)
        wind_speed = 8  # m/s average

        # Determine mixing intensity
        if wind_speed < wind_params['mixing_thresholds']['light_mixing']:
            mixing_intensity = 'calm'
        elif wind_speed < wind_params['mixing_thresholds']['moderate_mixing']:
            mixing_intensity = 'light'
        elif wind_speed < wind_params['mixing_thresholds']['strong_mixing']:
            mixing_intensity = 'moderate'
        else:
            mixing_intensity = 'strong'

        # Mixed layer depth
        mixed_layer_depth = wind_params['mixed_layer_depth'][mixing_intensity]

        # Effect on habitat based on depth relative to mixed layer
        if depth_positive < mixed_layer_depth:
            # Within mixed layer - enhanced productivity but more turbulent
            if depth_positive < mixed_layer_depth * 0.5:
                # Upper mixed layer - high turbulence
                mixing_effect = 0.9
            else:
                # Lower mixed layer - moderate effect
                mixing_effect = 1.1
        else:
            # Below mixed layer - stable conditions
            mixing_effect = 1.0

        # Thermocline disruption effect
        if wind_speed > wind_params['thermocline_disruption']['threshold_wind']:
            disruption_factor = wind_params['thermocline_disruption']['disruption_factor']
            if 80 < depth_positive < 120:  # Typical thermocline depth
                mixing_effect *= (1 - disruption_factor)

        return max(0.7, min(1.2, mixing_effect))

    def _calculate_multiscale_gradients(self, i, j, sst_data, chl_data):
        """Calculate gradients at multiple spatial scales"""
        gradients = {}
        scales = [1, 3, 5]  # Different spatial scales

        for scale in scales:
            # SST gradients
            sst_grad_x = self._sobel_gradient(i, j, sst_data, 'x', scale)
            sst_grad_y = self._sobel_gradient(i, j, sst_data, 'y', scale)
            sst_magnitude = np.sqrt(sst_grad_x**2 + sst_grad_y**2)

            # Chlorophyll gradients
            chl_grad_x = self._sobel_gradient(i, j, chl_data, 'x', scale)
            chl_grad_y = self._sobel_gradient(i, j, chl_data, 'y', scale)
            chl_magnitude = np.sqrt(chl_grad_x**2 + chl_grad_y**2)

            # Combined gradient
            combined_magnitude = np.sqrt(sst_magnitude**2 + chl_magnitude**2)

            gradients[scale] = {
                'sst': sst_magnitude,
                'chl': chl_magnitude,
                'combined': combined_magnitude,
                'direction': np.arctan2(sst_grad_y + chl_grad_y, sst_grad_x + chl_grad_x)
            }

        return gradients

    def _sobel_gradient(self, i, j, data, direction, scale):
        """Enhanced Sobel gradient calculation with scale"""
        rows, cols = data.shape

        # Boundary checks
        if i < scale or i >= rows - scale or j < scale or j >= cols - scale:
            return 0.0

        if direction == 'x':
            # Sobel X kernel scaled
            gradient = (
                -data[i-scale, j-scale] + data[i-scale, j+scale] +
                -2*data[i, j-scale] + 2*data[i, j+scale] +
                -data[i+scale, j-scale] + data[i+scale, j+scale]
            )
        else:  # direction == 'y'
            # Sobel Y kernel scaled
            gradient = (
                -data[i-scale, j-scale] - 2*data[i-scale, j] - data[i-scale, j+scale] +
                data[i+scale, j-scale] + 2*data[i+scale, j] + data[i+scale, j+scale]
            )

        return gradient / (8 * scale)

    def _canny_front_detection(self, gradients):
        """Canny-like edge detection for front identification"""
        # Use medium scale (3) for edge detection
        if 3 not in gradients:
            return 0.0

        combined_grad = gradients[3]['combined']

        # Threshold for significant gradient
        if combined_grad > 0.1:
            # Strong edge
            if combined_grad > 0.2:
                return 1.0
            # Moderate edge
            else:
                return 0.6
        else:
            return 0.0

    def _classify_front_strength(self, gradients, edge_strength):
        """Classify front strength (weak/moderate/strong)"""
        # Multi-scale strength assessment
        scale_weights = {1: 0.2, 3: 0.5, 5: 0.3}  # Weight medium scales more

        weighted_strength = 0
        for scale, weight in scale_weights.items():
            if scale in gradients:
                weighted_strength += gradients[scale]['combined'] * weight

        # Classify strength
        if weighted_strength > 0.3:
            strength_value = 1.0  # Strong
        elif weighted_strength > 0.15:
            strength_value = 0.7  # Moderate
        else:
            strength_value = 0.3  # Weak

        # Enhance with edge detection
        final_strength = strength_value * (0.7 + 0.3 * edge_strength)

        return final_strength

    def _calculate_frontal_uncertainty(self, gradients, persistence, strength):
        """Advanced uncertainty calculation for frontal zones"""
        # Base uncertainty
        base_uncertainty = 0.2

        # Reduce uncertainty for strong, persistent fronts
        strength_reduction = strength * 0.1
        persistence_reduction = persistence * 0.05

        # Calculate scale consistency
        scale_values = []
        for scale in [1, 3, 5]:
            if scale in gradients:
                scale_values.append(gradients[scale]['combined'])

        if len(scale_values) > 1:
            mean_val = np.mean(scale_values)
            std_val = np.std(scale_values)
            consistency = 1 - (std_val / (mean_val + 0.01)) if mean_val > 0 else 0
            consistency_penalty = (1 - max(0, consistency)) * 0.15
        else:
            consistency_penalty = 0.1

        total_uncertainty = base_uncertainty - strength_reduction - persistence_reduction + consistency_penalty

        return max(0.05, min(0.5, total_uncertainty))

    def _calculate_gradient(self, i, j, data):
        """Calculate spatial gradient at point (i,j)"""
        rows, cols = data.shape
        
        # Simple gradient calculation
        if i > 0 and i < rows-1 and j > 0 and j < cols-1:
            dx = (data[i, j+1] - data[i, j-1]) / 2
            dy = (data[i+1, j] - data[i-1, j]) / 2
            gradient = np.sqrt(dx**2 + dy**2)
        else:
            gradient = 0.1  # Default for edges
        
        return gradient
    
    def _calculate_statistics(self, hsi_grid, uncertainty_grid):
        """Calculate comprehensive statistics"""
        hsi_flat = hsi_grid.flatten()
        uncertainty_flat = uncertainty_grid.flatten()
        
        # Remove any NaN values
        valid_hsi = hsi_flat[~np.isnan(hsi_flat)]
        valid_uncertainty = uncertainty_flat[~np.isnan(uncertainty_flat)]
        
        if len(valid_hsi) == 0:
            return {'error': 'No valid HSI values'}
        
        stats = {
            'mean_hsi': float(np.mean(valid_hsi)),
            'max_hsi': float(np.max(valid_hsi)),
            'min_hsi': float(np.min(valid_hsi)),
            'std_hsi': float(np.std(valid_hsi)),
            'mean_uncertainty': float(np.mean(valid_uncertainty)),
            'habitat_zones': {
                'excellent': float(np.sum(valid_hsi > 0.8) / len(valid_hsi)),
                'good': float(np.sum((valid_hsi > 0.6) & (valid_hsi <= 0.8)) / len(valid_hsi)),
                'moderate': float(np.sum((valid_hsi > 0.4) & (valid_hsi <= 0.6)) / len(valid_hsi)),
                'poor': float(np.sum((valid_hsi > 0.2) & (valid_hsi <= 0.4)) / len(valid_hsi)),
                'unsuitable': float(np.sum(valid_hsi <= 0.2) / len(valid_hsi))
            },
            'total_cells': len(valid_hsi),
            'suitable_cells': int(np.sum(valid_hsi > 0.4))
        }
        
        return stats

    def temporal_habitat_analysis(self, study_area, date_ranges, species_list=None):
        """Perform temporal analysis across multiple time periods"""

        if species_list is None:
            species_list = ['great_white']

        print("📅 TEMPORAL HABITAT ANALYSIS")
        print("=" * 50)

        temporal_results = {}

        for species in species_list:
            print(f"\n🦈 Analyzing {self.shark_species_params[species]['name']}...")
            self.set_species(species)

            species_temporal = {}

            for period_name, date_range in date_ranges.items():
                print(f"   📊 Period: {period_name} ({date_range[0]} to {date_range[1]})")

                # Get environmental data for this period
                env_data, real_data = self.auto_download_nasa_data(study_area, date_range)

                # Run habitat prediction
                results = self.advanced_habitat_prediction(env_data)

                # Store results
                species_temporal[period_name] = {
                    'hsi_stats': results['statistics'],
                    'mean_hsi': results['statistics']['mean_hsi'],
                    'suitable_area': results['statistics']['suitable_cells'],
                    'date_range': date_range
                }

            temporal_results[species] = species_temporal

        # Analyze temporal patterns
        temporal_analysis = self._analyze_temporal_patterns(temporal_results)

        return temporal_results, temporal_analysis

    def _analyze_temporal_patterns(self, temporal_results):
        """Analyze patterns across time periods"""

        analysis = {}

        for species, periods in temporal_results.items():
            species_name = self.shark_species_params[species]['name']

            # Extract time series data
            period_names = list(periods.keys())
            hsi_values = [periods[p]['mean_hsi'] for p in period_names]
            suitable_areas = [periods[p]['suitable_area'] for p in period_names]

            # Calculate trends
            if len(hsi_values) > 1:
                hsi_trend = (hsi_values[-1] - hsi_values[0]) / len(hsi_values)
                area_trend = (suitable_areas[-1] - suitable_areas[0]) / len(suitable_areas)
            else:
                hsi_trend = 0
                area_trend = 0

            # Seasonal patterns (if applicable)
            seasonal_variation = np.std(hsi_values) if len(hsi_values) > 1 else 0

            analysis[species] = {
                'species_name': species_name,
                'hsi_trend': hsi_trend,
                'area_trend': area_trend,
                'seasonal_variation': seasonal_variation,
                'best_period': period_names[np.argmax(hsi_values)] if hsi_values else None,
                'worst_period': period_names[np.argmin(hsi_values)] if hsi_values else None,
                'mean_hsi_range': (min(hsi_values), max(hsi_values)) if hsi_values else (0, 0)
            }

        return analysis

    def analyze_shark_habitat(self, species, bounds, date_range):
        """
        Analyze shark habitat for specified species, region, and time period

        Args:
            species (str): Shark species ('great_white', 'tiger', 'bull', 'hammerhead', 'mako', 'blue')
            bounds (list): Geographic bounds [west, south, east, north] in decimal degrees
            date_range (tuple): Date range ('start_date', 'end_date') in 'YYYY-MM-DD' format

        Returns:
            dict: Complete analysis results with HSI grid, statistics, and metadata
        """
        print(f"\n🦈 ANALYZING {species.upper().replace('_', ' ')} SHARK HABITAT")
        print("=" * 60)

        # Set species for analysis
        original_species = self.current_species
        self.set_species(species)

        try:
            # Step 1: Download environmental data
            study_area = {
                'name': f'{species.replace("_", " ").title()} Shark Habitat Analysis',
                'bounds': bounds,
                'description': f'Habitat analysis for {species.replace("_", " ")} shark'
            }

            environmental_data, real_data_info = self.auto_download_nasa_data(study_area, date_range)

            # Step 2: Calculate the heuristic score surface.
            results = self.advanced_habitat_prediction(environmental_data)

            # Step 3: Add metadata
            results['analysis_metadata'] = {
                'species': species,
                'bounds': bounds,
                'date_range': date_range,
                'grid_size': len(results['hsi']),
                'data_sources': real_data_info,
                'analysis_timestamp': str(pd.Timestamp.now())
            }

            return results

        finally:
            # Restore original species
            self.set_species(original_species)

    def _calculate_hsi(self, temp_suit, prod_suit, frontal_suit, depth_suit, species=None):
        """
        Calculate Habitat Suitability Index using weighted geometric mean

        Args:
            temp_suit (numpy.ndarray): Temperature suitability grid (0-1)
            prod_suit (numpy.ndarray): Productivity suitability grid (0-1)
            frontal_suit (numpy.ndarray): Frontal zone suitability grid (0-1)
            depth_suit (numpy.ndarray): Depth suitability grid (0-1)
            species (str): Shark species for species-specific weights

        Returns:
            numpy.ndarray: HSI values (0-1)
        """
        if species is None:
            species = self.current_species

        # Species-specific weights
        weights = self.shark_species_params[species].get('hsi_weights', {
            'temperature': 0.30,
            'productivity': 0.25,
            'frontal': 0.25,
            'depth': 0.20
        })

        # Ensure all inputs have same shape
        shape = temp_suit.shape
        temp_suit = np.resize(temp_suit, shape)
        prod_suit = np.resize(prod_suit, shape)
        frontal_suit = np.resize(frontal_suit, shape)
        depth_suit = np.resize(depth_suit, shape)

        # Calculate weighted geometric mean
        # HSI = (T^w1 × P^w2 × F^w3 × D^w4)^(1/Σw)
        w_temp = weights['temperature']
        w_prod = weights['productivity']
        w_frontal = weights['frontal']
        w_depth = weights['depth']

        # Avoid zero values by adding small epsilon
        epsilon = 1e-10
        temp_suit = np.maximum(temp_suit, epsilon)
        prod_suit = np.maximum(prod_suit, epsilon)
        frontal_suit = np.maximum(frontal_suit, epsilon)
        depth_suit = np.maximum(depth_suit, epsilon)

        # Calculate HSI
        hsi = (
            (temp_suit ** w_temp) *
            (prod_suit ** w_prod) *
            (frontal_suit ** w_frontal) *
            (depth_suit ** w_depth)
        ) ** (1.0 / (w_temp + w_prod + w_frontal + w_depth))

        # Ensure HSI is in valid range [0, 1]
        hsi = np.clip(hsi, 0.0, 1.0)

        return hsi

def run_automatic_nasa_framework():
    """Run the command-line prototype demonstration."""
    
    print("🚀 SHARK HABITAT SUITABILITY PROTOTYPE")
    print("=" * 80)
    print("Deterministic heuristic demo; not validated ecological evidence")
    
    # Initialize framework with Great White as default
    framework = AutomaticNASAFramework('great_white')

    # Show species differentiation
    framework.explain_species_differentiation()

    # Define study area (California coast - Multi-species habitat)
    study_area = {
        'name': 'California Coast (Multi-Species Shark Habitat)',
        'bounds': [-125.0, 32.0, -115.0, 42.0],  # [west, south, east, north]
        'description': 'Prime shark habitat with upwelling zones and diverse bathymetry'
    }
    
    # Define date range (recent data)
    date_range = ('2024-01-01', '2024-01-31')
    
    # Step 1: Automatic NASA data download
    environmental_data, real_data_info = framework.auto_download_nasa_data(study_area, date_range)
    if environmental_data is None:
        print("No environmental prototype grid could be prepared.")
        return None
    
    # Step 2: Calculate the heuristic score surface.
    results = framework.advanced_habitat_prediction(environmental_data)
    
    # Step 3: Display results
    print("\n🦈 GREAT WHITE SHARK HABITAT ANALYSIS RESULTS")
    print("=" * 60)
    
    stats = results['statistics']
    print(f"📊 HABITAT SUITABILITY INDEX (HSI) RESULTS:")
    print(f"   Mean HSI: {stats['mean_hsi']:.3f} ± {stats['mean_uncertainty']:.3f}")
    print(f"   Maximum HSI: {stats['max_hsi']:.3f}")
    print(f"   Standard Deviation: {stats['std_hsi']:.3f}")
    print(f"   Total Analysis Cells: {stats['total_cells']:,}")
    print(f"   Cells Above 0.6: {stats['suitable_cells']:,}")
    
    print(f"\n🌊 PROTOTYPE SCORE DISTRIBUTION:")
    zones = stats['habitat_zones']
    print(f"   🟢 Very high (>0.8): {zones['excellent']:.1%}")
    print(f"   🔵 High (0.6-0.8): {zones['good']:.1%}")
    print(f"   🟡 Middle (0.4-0.6): {zones['moderate']:.1%}")
    print(f"   🟠 Low (0.2-0.4): {zones['poor']:.1%}")
    print(f"   🔴 Very low (<0.2): {zones['unsuitable']:.1%}")
    
    print(f"\n🛰️ INPUT PROVENANCE STATUS:")
    sst_info = environmental_data['sst']
    chl_info = environmental_data['chlorophyll']
    bath_info = environmental_data['bathymetry']
    print(f"   SST Data: {sst_info['source']}")
    print(f"   SST Evidence Status: {sst_info['accuracy']}")
    print(f"   SST Data Type: {sst_info['data_type']}")
    print(f"   Chlorophyll Data: {chl_info['source']}")
    print(f"   Chlorophyll Evidence Status: {chl_info['accuracy']}")
    print(f"   Chlorophyll Data Type: {chl_info['data_type']}")
    print(f"   Bathymetry Data: {bath_info['source']}")
    print(f"   Bathymetry Evidence Status: {bath_info['accuracy']}")
    print(f"   Bathymetry Quality: {bath_info['quality']}")
    
    print(f"\n🔬 EVIDENCE BOUNDARY:")
    print(f"   • Software and visualization prototype")
    print(f"   • Generated fallbacks are deterministic with seed {framework.seed}")
    print(f"   • No tagged-shark, field-survey, or ecological benchmark validation")
    print(f"   • Not suitable for safety, conservation, or policy decisions")

    return results

if __name__ == "__main__":
    results = run_automatic_nasa_framework()
