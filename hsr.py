# Import Libraries
import urllib.request
import re
import concurrent.futures
from threading import Lock
import os

# Utility Functions
def get_html(url):
    html = urllib.request.urlopen(url).read()
    html = str(html)
    return html

def clean_html(text):
    replace_list = [
        ('&#x27;', '\''),
        ('&quot;', '""'),
        ('\\n', ''),
        ('\\', '')
    ]
    text = re.sub(r'<[\s\S]*?>', '', text)
    for (old, new) in replace_list:
        text = text.replace(old, new)
    return text

# Workflow Functions
def get_character_details(character_order, character):
    name = character.split('/')[-1].replace('-', ' ').title()
    url = f'https://www.prydwen.gg{character}'
    html = get_html(url)
    json = {
        'No': character_order[0],
        'Name': name,
        'HP': '0',
        'ATK': '0',
        'DEF': '0',
        'Speed': '0',
        'CRIT Rate': '5',
        'CRIT DMG': '50',
        'Trace-HP': '0',
        'Trace-ATK': '0',
        'Trace-DEF': '0',
        'Trace-Speed': '0',
        'Trace-CRIT Rate': '0',
        'Trace-CRIT DMG': '0',
        'Trace-Effect RES': '0',
        'Trace-Effect HIT Rate': '0',
        'Trace-Physical DMG': '0',
        'Trace-Fire DMG': '0',
        'Trace-Ice DMG': '0',
        'Trace-Lightning DMG': '0',
        'Trace-Wind DMG': '0',
        'Trace-Quantum DMG': '0',
        'Trace-Imaginary DMG': '0',
        'Trace-A2': '',
        'Trace-A4': '',
        'Trace-A6': '',
        'E1': '',
        'E2': '',
        'E3': '',
        'E4': '',
        'E5': '',
        'E6': ''
    }

    # Stats
    stats = re.findall(r'<div class="details">([\d]+?)<!-- --></div>', html)
    for stat in zip(['HP', 'ATK', 'DEF', 'Speed'], stats):
        json[stat[0]] = stat[1]

    # Major Traces
    major_traces = re.findall(r'<div class="skill-icon[\s\S]*?">A2<!-- --><span>Major trace</span></div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p></div></div><div class="skill-with-coloring[\s\S]*?">([\s\S]+?)</div></div></div><div class="col"><div class="box"><div class="skill-header"><div class="skill-icon[\s\S]*?">A4<!-- --><span>Major trace</span></div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p></div></div><div class="skill-with-coloring[\s\S]*?">([\s\S]+?)</div></div></div><div class="col"><div class="box"><div class="skill-header"><div class="skill-icon[\s\S]*?">A6<!-- --><span>Major trace</span></div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p></div></div><div class="skill-with-coloring[\s\S]*?">([\s\S]+?)</div></div></div></div></div>', html)
    for trace in major_traces:
        json['Trace-A2'] = f'{clean_html(trace[0])}: {clean_html(trace[1])}'
        json['Trace-A4'] = f'{clean_html(trace[2])}: {clean_html(trace[3])}'
        json['Trace-A6'] = f'{clean_html(trace[4])}: {clean_html(trace[5])}'

    # Minor Traces
    minor_traces = re.findall(r'<span[\s\S]*?>(HP|ATK|DEF|Speed|CRIT Rate|CRIT DMG|Effect RES|Effect HIT Rate|Physical DMG|Fire DMG|Ice DMG|Lightning DMG|Wind DMG|Quantum DMG|Imaginary DMG)</span></div> <!-- --><span class="value">\+<!-- -->([\d.]+?)<!-- -->', html)
    for trace in minor_traces:
        json[f'Trace-{trace[0]}'] = trace[1]

    # Eidolons
    eidolons = re.findall(r'<div class="box"><div class="skill-header"><div class="skill-icon[\s\S]*?">E1</div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p><p class="skill-type">Eidolon 1</p></div></div><div class="skill-with-coloring eidolon[\s\S]*?"><p>([\s\S]+?)</p></div></div></div><div class="col"><div class="box"><div class="skill-header"><div class="skill-icon[\s\S]*?">E2</div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p><p class="skill-type">Eidolon 2</p></div></div><div class="skill-with-coloring eidolon[\s\S]*?"><p>([\s\S]+?)</p></div></div></div><div class="col"><div class="box"><div class="skill-header"><div class="skill-icon[\s\S]*?">E3</div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p><p class="skill-type">Eidolon 3</p></div></div><div class="skill-with-coloring eidolon[\s\S]*?"><p>([\s\S]+?)</p></div></div></div><div class="col"><div class="box"><div class="skill-header"><div class="skill-icon[\s\S]*?">E4</div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p><p class="skill-type">Eidolon 4</p></div></div><div class="skill-with-coloring eidolon[\s\S]*?"><p>([\s\S]+?)</p></div></div></div><div class="col"><div class="box"><div class="skill-header"><div class="skill-icon[\s\S]*?">E5</div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p><p class="skill-type">Eidolon 5</p></div></div><div class="skill-with-coloring eidolon[\s\S]*?"><p>([\s\S]+?)</p></div></div></div><div class="col"><div class="box"><div class="skill-header"><div class="skill-icon[\s\S]*?">E6</div><div class="skill-info"><p class="skill-name">([\s\S]+?)</p><p class="skill-type">Eidolon 6</p></div></div><div class="skill-with-coloring eidolon[\s\S]*?"><p>([\s\S]+?)</p></div></div></div></div></div>', html)
    for eidolon in eidolons:
        json['E1'] = f'{clean_html(eidolon[0])}: {clean_html(eidolon[1])}'
        json['E2'] = f'{clean_html(eidolon[2])}: {clean_html(eidolon[3])}'
        json['E3'] = f'{clean_html(eidolon[4])}: {clean_html(eidolon[5])}'
        json['E4'] = f'{clean_html(eidolon[6])}: {clean_html(eidolon[7])}'
        json['E5'] = f'{clean_html(eidolon[8])}: {clean_html(eidolon[9])}'
        json['E6'] = f'{clean_html(eidolon[10])}: {clean_html(eidolon[11])}'
    
    # Ascension Materials
    # No Skill Materials
    # ascension_materials = re.findall(r'<div class="hsr-name"><span>([\s\S]+?)</span>', html)[1:]

    # Output
    print(f'Updated: {name} ({character_order[0]} of {character_order[1]})', flush=True)
    return json

def get_light_cone_details(light_cone_order, light_cone_name, light_cone_rarity, light_cone_path, light_cone_stat, light_cone_effect, lock):
    name = clean_html(light_cone_name)
    json = {
        'No': light_cone_order[0],
        'Name' :name,
        'Rarity': light_cone_rarity,
        'Path': light_cone_path,
        'HP': light_cone_stat[0],
        'ATK': light_cone_stat[1],
        'DEF': light_cone_stat[2],
        'Effect': clean_html(light_cone_effect)
    }

    # Output
    with lock:
        print(f'Updated: {name} ({light_cone_order[0]} of {light_cone_order[1]})', flush=True)
        return json

def get_relic_set_details(relic_set_order, relic_set, lock):
    name = relic_set[0]
    effect = clean_html(relic_set[1])
    json = {
        'No': relic_set_order[0],
        'Name': name,
        'Two-Piece Effect': re.findall(r'\(2\) ([\s\S]+?)\(', effect)[0],
        'Four-Piece Effect': re.findall(r'\(4\) ([\s\S]+)', effect)[0]
    }

    # Output
    with lock:
        print(f'Updated: {name} ({relic_set_order[0]} of {relic_set_order[1]})', flush=True)
        return json

def get_planetary_ornament_set_details(planetary_ornament_set_order, planetary_ornament_set, lock):
    name = planetary_ornament_set[0]
    effect = clean_html(planetary_ornament_set[1])
    json = {
        'No': planetary_ornament_set_order[0],
        'Name': name,
        'Two-Piece Effect': effect[4:]
    }

    # Output
    with lock:
        print(f'Updated: {name} ({planetary_ornament_set_order[0]} of {planetary_ornament_set_order[1]})', flush=True)
        return json

def json_to_csv(json, file_name, lock):
    csv = ''

    for title in list(json[0].keys()):
        if ',' in title:
            title = f'"{title}"'
        csv += title + ','
    csv = csv[:-1] + '\n'
    
    for entry in json:
        for value in entry.values():
            if ',' in value:
                value = f'"{value}"'
            csv += value + ','
        csv = csv[:-1] + '\n'
    
    # Output
    with lock:
        file = open(file_name + '.csv', 'w')
        file.write(csv)
        file.close

        print(f'Exported: {file_name}.csv', flush=True)

# Thread Lock
lock = Lock()

# Execution
if __name__ == '__main__':
    # Characters
    print('Getting Characters Info...')

    # Lists
    character_html = get_html('https://www.prydwen.gg/star-rail/characters')
    character_elements = re.findall(r'href="(/star-rail/characters/[\s\S]+?)"', character_html)
    character_order = [(str(character_elements.index(character) + 1), str(len(character_elements))) for character in character_elements]
    
    # Process
    with concurrent.futures.ProcessPoolExecutor() as executor:
        character_details = list(executor.map(get_character_details, character_order, character_elements))
    
    print('')

    # Light Cones
    print('Getting Light Cones Info...')
    # Lists
    light_cone_html = get_html('https://www.prydwen.gg/star-rail/light-cones')
    light_cone_names = re.findall(r'<h4>([\s\S]+?)</h4>', light_cone_html)
    light_cone_rarities = re.findall(r'<strong class="rarity-hsr rarity-([345])', light_cone_html)
    light_cone_paths = re.findall(r'<strong>(Destruction|Hunt|Erudition|Harmony|Nihility|Preservation|Abundance)</strong>', light_cone_html)
    light_cone_stats = re.findall(r'<span>HP</span></div><strong>\+<!-- -->([\d]+?)<!-- --></strong></div>[\s\S]+?<span>ATK</span></div><strong>\+<!-- -->([\d]+?)<!-- --></strong></div>[\s\S]+?<span>DEF</span></div><strong>\+<!-- -->([\d]+?)<!-- --></strong></div>', light_cone_html)
    light_cone_effects = re.findall(r'<div class="hsr-cone-content"><div class="skill-with-coloring"><p>([\s\S]+?)</p></div></div>', light_cone_html)
    light_cone_count = len(light_cone_names)

    # Process
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_light_cone_details, (str(i + 1), light_cone_count), light_cone_names[i], light_cone_rarities[i], light_cone_paths[i], light_cone_stats[i], light_cone_effects[i], lock) for i in range(light_cone_count)]
        
        light_cone_details = []
        for future in concurrent.futures.as_completed(futures):
            light_cone_details.append(future.result())

    light_cone_details = sorted(light_cone_details, key=lambda x: x['Name'])

    print('')

    # Relics
    print('Getting Relics Info...\n')

    # Lists
    combined_relic_html = get_html('https://www.prydwen.gg/star-rail/guides/relic-sets')
    combined_relic_elements = re.findall(r'<h4>([\s\S]+?)</h4><div class="hsr-relic-info"><p>Type: <!-- --><strong>(Relic Set|Planetary Ornament Set)</strong></p></div></div></div><div class="hsr-relic-content"><div class="hsr-set-description[\s\S]*?"><div><span class="set-piece">([\s\S]+?)</div></div></div></div>', combined_relic_html)

    relic_set_elements = [(relic[0], relic[2]) for relic in combined_relic_elements if relic[1] == 'Relic Set']
    planetary_ornament_set_elements = [(relic[0], relic[2]) for relic in combined_relic_elements if relic[1] == 'Planetary Ornament Set']

    relic_set_count = len(relic_set_elements)
    planetary_ornament_set_count = len(planetary_ornament_set_elements)

    # Relic Sets
    print('Relic Sets:')

    # Process
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_relic_set_details, (str(i + 1), relic_set_count), relic_set_elements[i], lock) for i in range (relic_set_count)]
        
        relic_set_details = []
        for future in concurrent.futures.as_completed(futures):
            relic_set_details.append(future.result())

    relic_set_details = sorted(relic_set_details, key=lambda x: x['Name'])

    print('')

    # Planetary Ornament Sets
    print('Planetary Ornament Sets:')

    # Process
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_planetary_ornament_set_details, (str(i + 1), planetary_ornament_set_count), planetary_ornament_set_elements[i], lock) for i in range (planetary_ornament_set_count)]
        
        planetary_ornament_set_details =[]
        for future in concurrent.futures.as_completed(futures):
            planetary_ornament_set_details.append(future.result())

    planetary_ornament_set_details = sorted(planetary_ornament_set_details, key=lambda x: x['Name'])    

    print('')

    # Export to CSV
    print('Exporting...')

    # Lists
    json_list = [character_details, light_cone_details, relic_set_details, planetary_ornament_set_details]
    file_names = ['Character Database', 'Light Cone Database', 'Relic Set Database', 'Planetary Ornament Set Database']
    file_count = len(json_list)

    # Process
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(len(json_list)):
            executor.submit(json_to_csv, json_list[i], file_names[i], lock)

    print('\nDone\n')