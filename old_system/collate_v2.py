import sys
import xml.etree.ElementTree as ET
from copy import deepcopy
import os
import subprocess
from bs4 import BeautifulSoup, Comment
from collections import defaultdict

# Mapping of filenames to Apparatus Sigla
# htec.xml is the base text and is handled separately
FILE_SIGLA_MAP = {
    'htc.xml': 'C',
    'htna.xml': 'Na',
    'htnb.xml': 'Nb',
    'htp.xml': 'P',
    'htb.xml': 'B',
    'htk.xml': 'K',
    'htes.xml': 'EdS',
    'htet.xml': 'EdT'
}

# The preferred order for sorting sigla in the output
SIGLA_ORDER = ['C', 'Na', 'Nb', 'P', 'B', 'K', 'EdS', 'EdT']

def register_namespaces():
    """Register the TEI namespace to preserve it in output"""
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
    ET.register_namespace('xml', "http://www.w3.org/XML/1998/namespace")

def is_element_empty(element):
    """Check if an element is empty"""
    if element.text and element.text.strip():
        return False
    for child in element:
        if not is_element_empty(child):
            return False
    return True

def get_parent(root, element):
    """Find the parent of an element"""
    for parent in root.iter():
        for child in parent:
            if child == element:
                return parent
    return None

def remove_empty_divs(root):
    """Remove empty div elements from the tree"""
    to_remove = []
    for elem in root.findall('.//{http://www.tei-c.org/ns/1.0}div'):
        if is_element_empty(elem):
            to_remove.append(elem)
    
    for elem in reversed(to_remove):
        parent = get_parent(root, elem)
        if parent is not None:
            parent.remove(elem)

def process_tei_file(input_file, target_id):
    """
    Process TEI XML file, isolate the target ID, and remove standOff.
    Returns True if the target_id was found and file written, False otherwise.
    """
    try:
        output_file = f"temp.{input_file}"
        
        if not os.path.exists(input_file):
            print(f"Warning: Input file {input_file} not found.", file=sys.stderr)
            return False

        tree = ET.parse(input_file)
        root = tree.getroot()
        new_root = deepcopy(root)
        
        # Remove standOff elements
        standoff_ns = '{http://www.tei-c.org/ns/1.0}standOff'
        for standoff in new_root.findall(f'.//{standoff_ns}'):
            parent = get_parent(new_root, standoff)
            if parent is not None:
                parent.remove(standoff)

        # Check if target_id exists in this file before processing
        id_found = False
        elements_to_remove = []
        
        # We iterate to find the target and mark others for removal
        for elem in new_root.iter():
            xml_id = elem.get('{http://www.w3.org/XML/1998/namespace}id')
            if xml_id == target_id:
                id_found = True
            elif xml_id is not None:
                # Mark other IDs for removal
                elements_to_remove.append(elem)
        
        if not id_found:
            # If the ID isn't in this witness, we don't create a temp file
            # and return False so it's excluded from collation
            return False
        
        # Remove the elements that aren't the target
        for elem in reversed(elements_to_remove):
            parent = get_parent(new_root, elem)
            if parent is not None:
                parent.remove(elem)
        
        remove_empty_divs(new_root)
        
        tree = ET.ElementTree(new_root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        return True
        
    except Exception as e:
        print(f"An error occurred processing {input_file}: {e}", file=sys.stderr)
        return False

def generate_php_script(active_witness_files):
    """
    Generates a temporary PHP script that only includes the available witnesses.
    active_witness_files: list of filenames (e.g. 'htc.xml') that have the target ID.
    """
    php_content = [
        "<?php",
        "include 'upama/upama.php';",
        "$upama = new Upama();",
        "",
        "// Dynamic comparisons based on available witnesses"
    ]
    
    comparisons = []
    
    # We always compare against the base 'temp.htec.xml'
    # active_witness_files contains the source filenames. 
    # We need to prepend 'temp.' for the PHP script reading.
    
    for i, witness_file in enumerate(active_witness_files):
        var_name = f"$comparison{i+1}"
        # Upama compare syntax: compare(base, witness, params)
        line = f"{var_name} = $upama->compare('temp.htec.xml', 'temp.{witness_file}', '');"
        php_content.append(line)
        comparisons.append(var_name)
    
    # Create the array string: [$comparison1, $comparison2, ...]
    comp_array_str = "[" + ",".join(comparisons) + "]"
    
    php_content.extend([
        "",
        f"$collation = $upama->collate({comp_array_str});",
        "$stylesheet = 'upama/xslt/with_apparatus.xsl';",
        "echo $upama->transform($collation, $stylesheet);",
        "?>"
    ])
    
    with open("temp_collate.php", "w") as f:
        f.write("\n".join(php_content))

def extract_lemma(maintext_content, loc_info):
    """Extract lemma from maintext based on location information"""
    try:
        words = maintext_content.split()
        
        raw_start, raw_end = map(int, loc_info.split('x')[:2])
        if raw_start == raw_end:
            return words[0 if raw_start == 0 else raw_start - 1]
        
        start_pos = int(loc_info.split('x')[0]) - 1
        end_pos = int(loc_info.split('x')[1]) - 2
        
        lemma = ' '.join(words[start_pos:end_pos + 1])
        return lemma
    except (IndexError, ValueError) as e:
        # Silently fail for layout/extraction errors to avoid clutter
        return None

def process_apparatus(html_content, active_sigla):
    """
    Process the apparatus criticus.
    active_sigla: A list of sigla (strings) that are valid for this specific verse.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Filter the global order to only include sigla present in this run
    current_sigla_order = [s for s in SIGLA_ORDER if s in active_sigla]
    current_all_sigla = set(active_sigla)
    
    def sort_sigla(sigla):
        # Sort based on the global constant order
        return sorted(sigla, key=lambda x: SIGLA_ORDER.index(x) if x in SIGLA_ORDER else 999)
    
    # 1. Get Main Text
    maintext_div = soup.find('div', class_='maintext')
    maintext_content = ""
    if maintext_div:
        text_parts = []
        for content in maintext_div.children:
            if isinstance(content, str) and not isinstance(content, Comment):
                cleaned_text = content.strip()
                if cleaned_text:
                    text_parts.append(cleaned_text)
        
        verselines = maintext_div.find_all('div', class_='verseline')
        verse_texts = [line.get_text(strip=True) for line in verselines]
        
        all_parts = text_parts + verse_texts
        maintext_content = ' '.join(part for part in all_parts if part)
    
    variants = defaultdict(list)
    variant_sigla = defaultdict(set)
    
    # 2. Process Variants
    for varcontainer in soup.find_all('span', class_='varcontainer'):
        try:
            loc_info = varcontainer.get('data-loc')
            if not loc_info: continue
                
            lemma = extract_lemma(maintext_content, loc_info)
            if not lemma: continue
            
            variant_span = varcontainer.find('span', class_='variant')
            if not variant_span: continue
            
            editor_label = variant_span.find('span', class_='editor label')
            is_addition = editor_label and editor_label.get_text(strip=True).lower() == 'add'
            
            if is_addition:
                editor_label.decompose()
                variant_reading = f"ADD {variant_span.get_text(strip=True)} {lemma}"
            else:
                variant_reading = variant_span.get_text(strip=True)
            
            sigla = []
            for siglum_link in varcontainer.find_all('a', class_='msid'):
                s = siglum_link.get_text(strip=True)
                # Only include siglum if it's in our active list (sanity check)
                if s in current_all_sigla:
                    sigla.append(s)
            
            if not sigla: continue
                
            variants[lemma].append((variant_reading, sigla))
            variant_sigla[lemma].update(sigla)
            
        except Exception:
            continue
    
    # 3. Format Output
    formatted_variants = []
    for lemma, readings in variants.items():
        # Calculate witnesses supporting the lemma based ONLY on active sigla
        variant_mss = variant_sigla[lemma]
        lemma_sigla = current_all_sigla - variant_mss
        
        variant_str = f"{lemma}] "
        
        if not any("ADD" in reading for reading, _ in readings):
            # If all active witnesses agree on the lemma (no variants), 
            # or if the only variant witnesses are removed, this logic handles it.
            if len(variant_mss) == 0:
                # Should not happen if we are iterating variants, 
                # but technically possible if all variants were from excluded sigla
                continue 

            if len(lemma_sigla) == 0:
                 # Omits lemma witnesses if empty (all active witnesses have variants)
                 pass
            elif len(variant_mss) == 1 and len(lemma_sigla) > 1:
                # Convention: if many support lemma, maybe use Sigma? 
                # For now keeping your logic:
                variant_str += "Σ" # This implies 'All others'
            else:
                variant_str += " ".join(sort_sigla(lemma_sigla))
        
        readings_str = []
        for reading, sigla in readings:
            sigla_str = " ".join(sort_sigla(sigla))
            readings_str.append(f"{reading} {sigla_str}")
        
        formatted_variants.append(f"{variant_str} {'; '.join(readings_str)}")
    
    return maintext_content, formatted_variants

def run_collation(active_sigla):
    """Run the dynamically generated PHP script"""
    try:
        # Run the GENERATED temp_collate.php
        result = subprocess.run(['php', 'temp_collate.php'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        maintext, formatted_variants = process_apparatus(result.stdout, active_sigla)
        
        print("\nMain text:")
        print(maintext)
        
        print("\nApparatus criticus:")
        for variant in formatted_variants:
            print(variant)
            
        # Cleanup
        if os.path.exists("temp_collate.php"):
            os.remove("temp_collate.php")
            
        return formatted_variants
        
    except subprocess.CalledProcessError as e:
        print(f"Error running PHP: {e}", file=sys.stderr)
        print(f"PHP output: {e.output}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error processing collation: {e}", file=sys.stderr)
        raise

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <xml:id>", file=sys.stderr)
        sys.exit(1)
    
    target_id = sys.argv[1]
    register_namespaces()
    
    # 1. Process Base Text (htec.xml)
    # This MUST exist for collation to work
    if not process_tei_file('htec.xml', target_id):
        print(f"Error: Target ID '{target_id}' not found in base text (htec.xml). Aborting.", file=sys.stderr)
        sys.exit(1)

    # 2. Process Witnesses
    active_witness_files = []
    active_sigla = []
    
    # Iterate through our defined map to maintain order/knowledge of files
    for filename, siglum in FILE_SIGLA_MAP.items():
        if process_tei_file(filename, target_id):
            active_witness_files.append(filename)
            active_sigla.append(siglum)
    
    print(f"Found '{target_id}' in {len(active_witness_files)} witnesses: {', '.join(active_sigla)}")

    if not active_witness_files:
        print("No witnesses found containing the target ID (other than base).", file=sys.stderr)
        sys.exit(0)

    # 3. Generate Dynamic PHP Script
    generate_php_script(active_witness_files)
    
    # 4. Run Collation
    run_collation(active_sigla)

if __name__ == "__main__":
    main()
