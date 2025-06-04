from .state import State

def is_pet_template(obj: dict) -> bool:
    try:
        name = obj["m_displayName"]
        adj_list = obj["m_adjectiveList"]
        behaviors = obj["m_behaviors"]
    except KeyError:
        return False
    
    if b"EQUIP_Pet" not in adj_list:
        return False
    is_pet = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b"AdvancedPetBehavior":
            is_pet = True
            break
    
    return is_pet

class Pet:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        self.real_name = obj["m_objectName"]
        try:
            self.image = obj["m_sIcon"][0].split(b"/")[-1]
        except:
            self.image = ""
        behaviors = obj["m_behaviors"]
        pet_behavior = None
        item_behavior = None

        for behavior in behaviors:
            if behavior == None:
                continue

            match behavior["m_behaviorName"]:
                case b'AdvancedPetBehavior':
                    pet_behavior = behavior
                
                case b'ItemBehavior':
                    item_behavior = behavior

        self.max_guts = pet_behavior["m_nMaxGuts"]
        self.max_guile = pet_behavior["m_nMaxGuile"]
        self.max_grit = pet_behavior["m_nMaxGrit"]
        self.max_hp = pet_behavior["m_nMaxHP"]
        self.max_power = pet_behavior["m_nMaxPower"]
        self.max_agility = pet_behavior["m_nMaxAgility"]
        self.max_strength = pet_behavior["m_nMaxStrength"]
        self.max_will = pet_behavior["m_nMaxWill"]
        self.item_flags = item_behavior["m_itemFlags"]
        self.base_powers = []
        self.base_talents = []
        for power in pet_behavior["m_powers"]:
            self.base_powers.append(power)
        for talent in pet_behavior["m_talents"]:
            self.base_talents.append(talent)
        self.preferred_snacks = []
        for snack in pet_behavior["m_preferredSnacks"]:
            snack_split = snack.split(b"_")
            snack_type = snack_split[1]
            try:
                snack_type_type = snack_split[2]
            except:
                snack_type_type = b""
            snack_string = snack_type + snack_type_type
            self.preferred_snacks.append(snack_string)