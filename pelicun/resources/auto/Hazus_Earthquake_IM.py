# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Leland Stanford Junior University
# Copyright (c) 2023 The Regents of the University of California
#
# This file is part of pelicun.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# You should have received a copy of the BSD 3-Clause License along with
# pelicun. If not, see <http://www.opensource.org/licenses/>.
#
# Contributors:
# Adam Zsarnóczay

import pandas as pd

ap_DesignLevel = {
    1940: 'PC',
    1940: 'LC',
    1975: 'MC',
    2100: 'HC'
}

ap_DesignLevel_W1 = {
       0: 'PC',
       0: 'LC',
    1975: 'MC',
    2100: 'HC'
}

ap_Occupancy = {
    'Other/Unknown': 'RES3',
    'Residential - Single-Family': 'RES1',
    'Residential - Town-Home': 'RES3',
    'Residential - Multi-Family': 'RES3',
    'Residential - Mixed Use': 'RES3',
    'Office': 'COM4',
    'Hotel': 'RES4',
    'School': 'EDU1',
    'Industrial - Light': 'IND2',
    'Industrial - Warehouse': 'IND2',
    'Industrial - Heavy': 'IND1',
    'Retail': 'COM1',
    'Parking' : 'COM10'
}

def convertBridgeToHAZUSclass(AIM):

    #TODO: replace labels in AIM with standard CamelCase versions
    structureType = AIM["BridgeClass"]
    # if type(structureType)== str and len(structureType)>3 and structureType[:3] == "HWB" and 0 < int(structureType[3:]) and 29 > int(structureType[3:]):
    #     return AIM["bridge_class"]
    state = AIM["StateCode"]
    yr_built = AIM["YearBuilt"] 
    num_span = AIM["NumOfSpans"]
    len_max_span = AIM["MaxSpanLength"] 

    seismic = ((int(state)==6 and int(yr_built)>=1975) or 
               (int(state)!=6 and int(yr_built)>=1990))

    # Use a catch-all, other class by default
    bridge_class = "HWB28"
    
    if len_max_span > 150:
        if not seismic:
            bridge_class = "HWB1"
        else:
            bridge_class = "HWB2"

    elif num_span == 1:
        if not seismic:
            bridge_class = "HWB3"
        else:
            bridge_class = "HWB4"

    elif structureType in list(range(101,107)):
        if not seismic:
            if state != 6:
                bridge_class = "HWB5"
            else:
                bridge_class = "HWB6"
        else:
            bridge_class = "HWB7"

    elif structureType in [205,206]:
        if not seismic:
            bridge_class = "HWB8"
        else:
            bridge_class = "HWB9"

    elif structureType in list(range(201,207)):
        if not seismic:
            bridge_class = "HWB10"
        else:
            bridge_class = "HWB11"

    elif structureType in list(range(301,307)):
        if not seismic:
            if len_max_span>=20:
                if state != 6:
                    bridge_class = "HWB12"
                else:
                    bridge_class = "HWB13"
            else:
                if state != 6:
                    bridge_class = "HWB24"
                else:
                    bridge_class = "HWB25"
        else:
            bridge_class = "HWB14"

    elif structureType in list(range(402,411)):
        if not seismic:
            if len_max_span>=20:
                bridge_class = "HWB15"
            elif state != 6:
                bridge_class = "HWB26"
            else:
                bridge_class = "HWB27"
        else:
            bridge_class = "HWB16"

    elif structureType in list(range(501,507)):
        if not seismic:
            if state != 6:
                bridge_class = "HWB17"
            else:
                bridge_class = "HWB18"
        else:
            bridge_class = "HWB19"

    elif structureType in [605,606]:
        if not seismic:
            bridge_class = "HWB20"
        else:
            bridge_class = "HWB21"

    elif structureType in list(range(601,608)):
        if not seismic:
            bridge_class = "HWB22"
        else:
            bridge_class = "HWB23"
    
    
    #TODO: review and add HWB24-27 rules
    #TODO: also double check rules for HWB10-11 and HWB22-23

    return bridge_class


    # original code by JZ
    """
    if not seismic and len_max_span > 150:
        return "HWB1"
    elif seismic and len_max_span > 150:
        return "HWB2"
    elif not seismic and num_span == 1:
        return "HWB3"
    elif seismic and num_span == 1:
        return "HWB4"
    elif not seismic and 101 <= structureType and structureType <= 106 and state != 6:
        return "HWB5"
    elif not seismic and 101 <= structureType and structureType <= 106 and state ==6:
        return "HWB6"
    elif seismic and 101 <= structureType and structureType <= 106:
        return "HWB7"
    elif not seismic and 205 <= structureType and structureType <= 206:
        return "HWB8"
    elif seismic and 205 <= structureType and structureType <= 206:
        return "HWB9"
    elif not seismic and 201 <= structureType and structureType <= 206:
        return "HWB10"
    elif seismic and 201 <= structureType and structureType <= 206:
        return "HWB11"
    elif not seismic and 301 <= structureType and structureType <= 306 and state != 6:
        return "HWB12"
    elif not seismic and 301 <= structureType and structureType <= 306 and state == 6:
        return "HWB13"
    elif seismic and 301 <= structureType and structureType <= 306:
        return "HWB14"
    elif not seismic and 402 <= structureType and structureType <= 410:
        return "HWB15"
    elif seismic and 402 <= structureType and structureType <= 410:
        return "HWB16"
    elif not seismic and 501 <= structureType and structureType <= 506 and state != 6:
        return "HWB17"
    elif not seismic and 501 <= structureType and structureType <= 506 and state == 6:
        return "HWB18"
    elif seismic and 501 <= structureType and structureType <= 506:
        return "HWB19"
    elif not seismic and 605 <= structureType and structureType <= 606:
        return "HWB20"
    elif seismic and 605 <= structureType and structureType <= 606:
        return "HWB21"
    elif not seismic and 601 <= structureType and structureType <= 607:
        return "HWB22"
    elif seismic and 601 <= structureType and structureType <= 607:
        return "HWB23"

    elif not seismic and 301 <= structureType and structureType <= 306 and state != 6:
        return "HWB24"
    elif not seismic and 301 <= structureType and structureType <= 306 and state == 6:
        return "HWB25"
    elif not seismic and 402 <= structureType and structureType <= 410 and state != 6:
        return "HWB26"
    elif not seismic and 402 <= structureType and structureType <= 410 and state == 6:
        return "HWB27"
    else:
        return "HWB28"
    """

def convertTunnelToHAZUSclass(AIM):

    if ("Bored" in AIM["ConstructType"]) or ("Drilled" in AIM["ConstructType"]):
        return "HTU1"
    elif ("Cut" in AIM["ConstructType"]) or ("Cover" in AIM["ConstructType"]):
        return "HTU2"
    else:
        # Select HTU2 for unclassfied tunnels because it is more conservative. 
        return "HTU2" 

def convertRoadToHAZUSclass(AIM):

    if AIM["RoadType"] in ["Primary", "Secondary"]:
        return "HRD1"

    elif AIM["RoadType"]=="Residential":
        return "HRD2"

    else:
        # many unclassified roads are urban roads
        return "HRD2" 

def convert_story_rise(structureType, stories):


    if structureType in ['W1', 'W2', 'S3', 'PC1', 'MH']:

        # These archetypes have no rise information in their IDs
        rise = None

    else:

        # First, check if we have valid story information
        try:

            stories = int(stories)

        except:

            raise ValueError('Missing "NumberOfStories" information, '
                             'cannot infer rise attribute of archetype')

        if structureType == 'RM1':

            if stories <= 3:
                rise = "L"

            else:
                rise = "M"

        elif structureType == 'URM':
            if stories <= 2:
                rise = "L"

            else:
                rise = "M"

        elif structureType in ['S1', 'S2', 'S4', 'S5', 'C1', 'C2', 'C3', \
                               'PC2', 'RM2']:
            if stories <=3:
                rise = "L"

            elif stories <= 7:
                rise = "M"

            else:
                rise = "H"
            
    return rise

def auto_populate(AIM):
    """
    Automatically creates a performance model for PGA-based Hazus EQ analysis.

    Parameters
    ----------
    AIM: dict
        Asset Information Model - provides features of the asset that can be 
        used to infer attributes of the performance model.

    Returns
    -------
    GI_ap: dict
        Extended General Information - extends the GI from the input AIM with 
        additional inferred features. These features are typically used in 
        intermediate steps during the auto-population and are not required 
        for the performance assessment. They are returned to allow reviewing 
        how these latent variables affect the final results.
    DL_ap: dict
        Damage and Loss parameters - these define the performance model and 
        details of the calculation.
    CMP: DataFrame
        Component assignment - Defines the components (in rows) and their 
        location, direction, and quantity (in columns).
    """

    # extract the General Information
    GI = AIM.get('GeneralInformation', None)

    if GI==None:
        #TODO: show an error message
        pass

    # initialize the auto-populated GI
    GI_ap = GI.copy()

    assetType = AIM["assetType"]
    ground_failure = AIM["Applications"]["DL"]["ApplicationData"]["ground_failure"]

    if assetType=="Buildings":

        # get the building parameters
        bt = GI['StructureType'] #building type

        # get the design level
        dl = GI.get('DesignLevel', None)

        if dl == None:
            # If there is no DesignLevel provided, we assume that the YearBuilt is
            # available
            year_built = GI['YearBuilt']

            if 'W1' in bt:
                DesignL = ap_DesignLevel_W1
            else:
                DesignL = ap_DesignLevel
            
            for year in sorted(DesignL.keys()):
                if year_built <= year:
                    dl = DesignL[year]            
                    break

            GI_ap['DesignLevel'] = dl

        # get the number of stories / height
        stories = GI.get('NumberOfStories', None)

        # We assume that the structure type does not include height information
        # and we append it here based on the number of story information
        rise = convert_story_rise(bt, stories)

        if rise is not None:
            LF = f'LF.{bt}.{rise}.{dl}'
            GI_ap['BuildingRise'] = rise
        else:
            LF = f'LF.{bt}.{dl}'


        CMP = pd.DataFrame(
                {f'{LF}': [  'ea',         1,          1,        1,   'N/A']},
                index = [         'Units','Location','Direction','Theta_0','Family']
            ).T

        # if needed, add components to simulate damage from ground failure
        if ground_failure:

            foundation_type = 'S'

            FG_GF_H = f'GF.H.{foundation_type}'
            FG_GF_V = f'GF.V.{foundation_type}'
            
            CMP_GF = pd.DataFrame(
                {f'{FG_GF_H}':[  'ea',         1,          1,        1,   'N/A'],
                 f'{FG_GF_V}':[  'ea',         1,          3,        1,   'N/A']},
                index = [     'Units','Location','Direction','Theta_0','Family']
            ).T

            CMP = pd.concat([CMP, CMP_GF], axis=0)

        # set the number of stories to 1
        # there is only one component in a building-level resolution
        stories = 1

        # get the occupancy class
        if GI['OccupancyClass'] in ap_Occupancy.keys():
            ot = ap_Occupancy[GI['OccupancyClass']]
        else:
            ot = GI['OccupancyClass']
        
        DL_ap = {
            "Asset": {
                "ComponentAssignmentFile": "CMP_QNT.csv",
                "ComponentDatabase": "Hazus Earthquake - Buildings",
                "NumberOfStories": f"{stories}",
                "OccupancyType": f"{ot}",
                "PlanArea": "1"
            },
            "Damage": {
                "DamageProcess": "Hazus Earthquake"
            },
            "Demands": {        
            },
            "Losses": {
                "BldgRepair": {
                    "ConsequenceDatabase": "Hazus Earthquake - Buildings",
                    "MapApproach": "Automatic"
                }
            }
        }

    elif assetType == "TransportationNetwork":

        inf_type = GI["assetSubtype"]
        
        if inf_type == "HwyBridge":

            # get the bridge class
            bt = convertBridgeToHAZUSclass(GI)
            GI_ap['BridgeHazusClass'] = bt

            CMP = pd.DataFrame(
                {f'HWB.GS.{bt[3:]}': [  'ea',         1,          1,        1,   'N/A'],
                 f'HWB.GF':          [  'ea',         1,          1,        1,   'N/A']},
                index = [            'Units','Location','Direction','Theta_0','Family']
            ).T

            DL_ap = {
                "Asset": {
                    "ComponentAssignmentFile": "CMP_QNT.csv",
                    "ComponentDatabase": "Hazus Earthquake - Transportation",
                    "BridgeHazusClass": bt,
                    "PlanArea": "1"
                },
                "Damage": {
                    "DamageProcess": "Hazus Earthquake"
                },
                "Demands": {        
                },
                "Losses": {
                    "BldgRepair": {
                        "ConsequenceDatabase": "Hazus Earthquake - Transportation",
                        "MapApproach": "Automatic"
                    }
                }
            }

        elif inf_type == "HwyTunnel":

            # get the tunnel class
            tt = convertTunnelToHAZUSclass(GI)
            GI_ap['TunnelHazusClass'] = tt

            CMP = pd.DataFrame(
                {f'HTU.GS.{tt[3:]}': [  'ea',         1,          1,        1,   'N/A'],
                 f'HTU.GF':          [  'ea',         1,          1,        1,   'N/A']},
                index = [            'Units','Location','Direction','Theta_0','Family']
            ).T

            DL_ap = {
                "Asset": {
                    "ComponentAssignmentFile": "CMP_QNT.csv",
                    "ComponentDatabase": "Hazus Earthquake - Transportation",
                    "TunnelHazusClass": tt,
                    "PlanArea": "1"
                },
                "Damage": {
                    "DamageProcess": "Hazus Earthquake"
                },
                "Demands": {        
                },
                "Losses": {
                    "BldgRepair": {
                        "ConsequenceDatabase": "Hazus Earthquake - Transportation",
                        "MapApproach": "Automatic"
                    }
                }
            }
        elif inf_type == "Roadway":

            # get the road class
            rt = convertRoadToHAZUSclass(GI)
            GI_ap['RoadHazusClass'] = rt

            CMP = pd.DataFrame(
                {f'HRD.GF.{rt[3:]}':[  'ea',         1,          1,        1,   'N/A']},
                index = [           'Units','Location','Direction','Theta_0','Family']
            ).T

            DL_ap = {
                "Asset": {
                    "ComponentAssignmentFile": "CMP_QNT.csv",
                    "ComponentDatabase": "Hazus Earthquake - Transportation",
                    "RoadHazusClass": rt,
                    "PlanArea": "1"
                },
                "Damage": {
                    "DamageProcess": "Hazus Earthquake"
                },
                "Demands": {        
                },
                "Losses": {
                    "BldgRepair": {
                        "ConsequenceDatabase": "Hazus Earthquake - Transportation",
                        "MapApproach": "Automatic"
                    }
                }
            }
        else:
            print("subtype not supported in HWY")

    elif assetType == "WaterDistributionNetwork":
        
        pipe_material_map ={"CI": "B", "AC": "B", "RCC": "B",
                            "DI": "D", "PVC": "D",
                            "DS": "B",
                            "BS": "D",}
        
        #GI = AIM.get("GeneralInformation", None)
        #if GI==None:
            
        
        # initialize the auto-populated GI
        wdn_element_type = GI_ap.get("type", "MISSING")
        asset_name = GI_ap.get("AIM_id", None)
        
        
        if wdn_element_type == "Pipe":
            pipe_construction_year = GI_ap.get("year", None)
            pipe_diameter = GI_ap.get("diameter", None)
            #diamaeter value is a fundamental part of hydraulic performance assessment
            if pipe_diameter == None:
                raise ValueError(f"pipe diamater in asset type {assetType}, \
                                 asset id \"{asset_name}\" has no diameter \
                                     value.")
            
            pipe_length = GI_ap.get("length", None)
            #length value is a fundamental part of hydraulic performance assessment
            if pipe_diameter == None:
                raise ValueError(f"pipe length in asset type {assetType}, \
                                 asset id \"{asset_name}\" has no diameter \
                                     value.")
            
            pipe_material = GI_ap.get("material", "missing")
            
            #pipe material can be not available or named "missing" in both case, pipe flexibility will be set to "missing"
            
            """
            The assumed logic is that if the material is missing, if the pipe
            is smaller than or equal to 20 inches, the material is Cast Iron
            (CI) otherwise the pipe material is steel.
                If the material is steel (ST), either based on user specified
            input or the assumption due to the lack of the user-input, the year
            that the pipe is constructed define the flexibility status per HAZUS
            instructions. If the pipe is built in 1935 or after, it is, the pipe
            is Ductile Steel (DS), and otherwise it is Brittle Steel (BS).
                If the pipe is missing construction year and is built by steel,
            we assume consevatively that the pipe is brittle (i.e., BS)
            """
            if pipe_material == "missing":
                if pipe_diameter > 20 * 0.0254: #20 inches in meter
                    print(f"Asset {asset_name} is missing material. Material is\
                          assumed to be Cast Iron")
                    pipe_material = "CI"
                else:
                    print(f"Asset {asset_name} is missing material. Material is\
                          assumed to be Steel (ST)")
                    pipe_material = "ST"
                          
            if pipe_material == "ST":
                if pipe_construction_year >= 1935:
                    print(f"Asset {asset_name} has material of \"ST\" is assumed to be\
                          Ductile Steel")
                    pipe_material = "DS"
                else:
                    print(f"Asset {asset_name} has material of \"ST\" is assumed to be\
                          Brittle Steel")
                    pipe_material = "BS"
            
            pipe_flexibility = pipe_material_map.get(pipe_material, "missing")
            
            GI_ap["material flexibility"] = pipe_flexibility
            GI_ap["material"] = pipe_material
            
            CMP = pd.DataFrame(
                {f'PWP.{pipe_flexibility}.GS': ['ea', 1, 1, pipe_length, 'N/A'],
                 f'PWP.{pipe_flexibility}.GF': ['ea', 1, 1, pipe_length, 'N/A']},
                index = ['Units','Location','Direction','Theta_0','Family']
            ).T
            
            DL_ap = {
                "Asset": {
                    "ComponentAssignmentFile": "CMP_QNT.csv",
                    "ComponentDatabase": "Hazus Earthquake - Water",
                    "Material Flexibility": pipe_flexibility,
                    "PlanArea": "1" # Sina: does not make sense for water. Kept it here since itw as also kept here for Transportation
                },
                "Damage": {
                    "DamageProcess": "Hazus Earthquake"
                },
                "Demands": {        
                },
                "Losses": {
                    # We don't have this
                    #"BldgRepair": {
                        #"ConsequenceDatabase": "Hazus Earthquake - Transportation",
                        #"MapApproach": "Automatic"
                    #}
                }
            }
        
        elif wdn_element_type == "Tank":
            
            tank_cmp_lines = {
                ("OG", "C", 1):{'PST.G.C.A.GS': [ 'ea', 1, 1, 1, 'N/A' ]},
                ("OG", "C", 0):{'PST.G.C.U.GS': [ 'ea', 1, 1, 1, 'N/A' ]},
                ("OG", "S", 1):{'PST.G.S.A.GS': [ 'ea', 1, 1, 1, 'N/A' ]},
                ("OG", "S", 0):{'PST.G.S.U.GS': [ 'ea', 1, 1, 1, 'N/A' ]},
                #Anchored status and Wood is not defined for On Ground tanks
                ("OG", "W", 0):{'PST.G.W.GS':   [ 'ea', 1, 1, 1, 'N/A' ]},
                #Anchored status and Steel is not defined for Above Ground tanks
                ("AG", "S", 0):{'PST.A.S.GS':   [ 'ea', 1, 1, 1, 'N/A' ]},
                #Anchored status and Concrete is not defined for Buried tanks.
                ("B", "C", 0):{'PST.B.C.GF':    [ 'ea', 1, 1, 1, 'N/A' ]}
                }
                
            """
            The default values are assumed: material = Concrete (C),
            location= On Ground (OG), and Anchored = 1 
            """
            tank_material = GI_ap.get("material", "C")
            tank_location = GI_ap.get("location", "OG")
            tank_anchored = GI_ap.get("anchored", int(1) )
            
            tank_material_allowable = {"C", "S"}
            if tank_material not in tank_material_allowable:
                raise ValueError(f"Tank's material = \"{tank_material}\" is \
                                 not allowable in tank {asset_name}. The \
                                 material must be either C for concrete or S \
                                 for steel.")
            
            tank_location_allowable = {"AG", "OG", "B"}
            if tank_location not in tank_location_allowable:
                raise ValueError(f"Tank's location = \"{tank_location}\" is \
                                 not allowable in tank {asset_name}. The \
                                 location must be either \"AG\" for Above \
                                 ground, \"OG\" for On Ground or \"BG\" for \
                                 Bellow Ground (burried) Tanks.")
            
            tank_anchored_allowable = {int(0), int(1)}
            if tank_anchored not in tank_anchored_allowable:
                raise ValueError(f"Tank's anchored status = \"{tank_location}\
                                 \" is not allowable in tank {asset_name}. \
                                     The anchored status must be either integer\
                                     value 0 for unachored, or 1 for anchored")
            
            if tank_location == "AG" and tank_material == "C":
                print(f"The tank {asset_name} is Above Ground (i.e., AG), but \
                      the material type is Concrete (\"C\"). Tank type \"C\" is not \
                    defiend for AG tanks. The tank is assumed to be Steel (\"S\")")
                tank_material = "S"
            
            if tank_location == "AG" and tank_material == "W":
                print(f"The tank {asset_name} is Above Ground (i.e., AG), but \
                      the material type is Wood (\"W\"). Tank type \"W\" is not \
                    defiend for AG tanks. The tank is assumed to be Steel (\"S\")")
                tank_material = "S"

            
            if tank_location == "B" and tank_material == "S":
                print(f"The tank {asset_name} is burried (i.e., B), but the\
                      material type is Steel (\"S\"). Tank type \"S\" is not defiend for\
                      B tanks. The tank is assumed to be Concrete (\"C\")")
                tank_material = "C"
            
            if tank_location == "B" and tank_material == "W":
                print(f"The tank {asset_name} is burried (i.e., B), but the\
                      material type is Wood (\"W\"). Tank type \"W\" is not defiend for\
                      B tanks. The tank is assumed to be Concrete (\"C\")")
                tank_material = "C"
                
            if tank_anchored == 1:
                 #Since anchore status does nto matter, there is no need to
                 #print a warning
                 tank_anchored = 0
                
            cur_tank_cmp_line = tank_cmp_lines[(tank_location, tank_material, tank_anchored)]
            
            CMP = pd.DataFrame(
                cur_tank_cmp_line,
                index = ['Units','Location','Direction','Theta_0','Family']
            ).T
            
            DL_ap = {
                "Asset": {
                    "ComponentAssignmentFile": "CMP_QNT.csv",
                    "ComponentDatabase": "Hazus Earthquake - Water",
                    "Material": tank_material,
                    "Location": tank_location,
                    "Anchored": tank_anchored,
                    "PlanArea": "1" # Sina: does not make sense for water. Kept it here since itw as also kept here for Transportation
                },
                "Damage": {
                    "DamageProcess": "Hazus Earthquake"
                },
                "Demands": {        
                },
                "Losses": {
                    # We don't have this
                    #"BldgRepair": {
                        #"ConsequenceDatabase": "Hazus Earthquake - Transportation",
                        #"MapApproach": "Automatic"
                    #}
                }
            }
            
                 
            
                 
            
            
        else:
            print(f"Water Distribution network element type {wdn_element_type} is not supported in Hazus Earthquake IM DL method")

    else:
        print(f"AssetType: {assetType} is not supported in Hazus Earthquake IM DL method")

    return GI_ap, DL_ap, CMP