import re
import json

# Ваш фрагмент данных
test_data = """
  - name: STR_CONTACT_SMUGGLERS
    cost: 15
    points: -200
    dependencies:
      - STR_CONTACT_CAR_THIEVES
      - STR_LAPUTA
      - STR_SMUGGLER
      - STR_CAPTAINS_RANK_03
    unlocks:
      - STR_ADVANCED_WEAPONS
  - name: STR_CONTACT_MUTANT_ALLIANCE
    cost: 10
    points: 1500
    dependencies:
      - STR_ALIEN_ORIGINS
      - STR_MUTANT_ORIGINS
      - STR_LOGISTICS
      - STR_ALIEN_TERROR
      - STR_TROPHY_TARGET_75_MUTANT_ALLIANCE
      - STR_BOUNTY_HUNTING_PRIZE_ALLIANCE_FAVORS
      - STR_CAPTAINS_RANK_04
    unlocks:
      - STR_SCHOOL_BOOKS
      - STR_DURASUIT_PROCUREMENT_PREQ
      - STR_MUTANT_ALLIANCE_LORE
      - STR_ZERO_ZERO_PREQ
      - STR_HYBRID_RECRUITMENT
    disables:
      - STR_RECRUIT_PUREBLOODS
  - name: STR_CONTACT_MAGIC_SHOP
    cost: 25
    points: 100
    dependencies:
      - STR_WITCH_CONVERSATIONS
      - STR_PERSUASION
  - name: STR_CONTACT_MERCENARIES
    cost: 50
    points: 100
    dependencies:
      - STR_CONTACT_MERCENARIES_PREQ
      - STR_CONTACT_EUROSYNDICATE
      - STR_DIPLOMACY
      - STR_LEADER_PLUS
      - STR_SECTOID
      - STR_FLOATER
      - STR_SNAKEMAN
      - STR_CAPTAINS_RANK_08
"""

def parse_fragment(content):
    """Имитация логики из parser.py"""
    entries = re.finditer(r'^\s*-\s+name:\s*(STR_[A-Z0-9_]+)(.*?)(?=^\s*-\s+name:|\Z)', content, re.DOTALL | re.MULTILINE)
    raw = {}
    
    for m in entries:
        t_id = m.group(1)
        block = m.group(2)
        
        # Пропускаем удаленные записи
        if 'delete:' in block[:20]:
            continue
            
        def get_list(keyword):
            pattern = rf'{keyword}:(.*?)(?=\n\s*[a-z]|$)'
            match = re.search(pattern, block, re.DOTALL)
            if match:
                return re.findall(r'(STR_[A-Z0-9_]+)', match.group(1))
            return []
        
        raw[t_id] = {
            "deps": list(set(get_list("dependencies"))),
            "unlocks": list(set(get_list("unlocks")))
            # Обратите внимание: поле 'disables' сейчас игнорируется!
        }
    
    return raw

result = parse_fragment(test_data)
print(json.dumps(result, indent=2, ensure_ascii=False))
