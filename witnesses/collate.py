import sys
import xml.etree.ElementTree as ET
from copy import deepcopy
import os
import subprocess
from bs4 import BeautifulSoup, Comment
import re
from collections import defaultdict

def register_namespaces():
    """Register the TEI namespace to preserve it in output"""
    ET.register_namespace('', "http://www.tei-c.org/ns/1.0")
    ET.register_namespace('xml', "http://www.w3.org/XML/1998/namespace")

def is_element_empty(element):
    """Check if an element is empty (has no content or only empty child elements)"""
    if element.text and element.text.strip():
        return False
    for child in element:
        if not is_element_empty(child):
            return False
    return True

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
    """Process TEI XML file to extract specific xml:id and its context"""
    try:
        output_file = f"temp.{input_file}"
        
        tree = ET.parse(input_file)
        root = tree.getroot()
        new_root = deepcopy(root)
        
        elements_to_remove = []
        for elem in new_root.iter():
            xml_id = elem.get('{http://www.w3.org/XML/1998/namespace}id')
            if xml_id is not None and xml_id != target_id:
                elements_to_remove.append(elem)
        
        for elem in reversed(elements_to_remove):
            parent = get_parent(new_root, elem)
            if parent is not None:
                parent.remove(elem)
        
        remove_empty_divs(new_root)
        
        tree = ET.ElementTree(new_root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        # print(f"Successfully processed {input_file} for ID: {target_id}")
        
    except ET.ParseError as e:
        print(f"Error parsing XML file {input_file}: {e}", file=sys.stderr)
        raise
    except FileNotFoundError:
        print(f"Input file {input_file} not found", file=sys.stderr)
        raise
    except Exception as e:
        print(f"An error occurred processing {input_file}: {e}", file=sys.stderr)
        raise

def get_parent(root, element):
    """Find the parent of an element"""
    for parent in root.iter():
        for child in parent:
            if child == element:
                return parent
    return None

def extract_lemma(maintext_content, loc_info):
    """
    Extract lemma from maintext based on location information
    
    Args:
        maintext_content (str): The main text content
        loc_info (str): Location information (e.g., "2x3" means word 2, "2x4" means words 2-3)
                       Special case "0x0" means first word
    
    Returns:
        str: The extracted lemma
    """
    try:
        # Split text into words
        words = maintext_content.split()
        
        # Handle special case for additions for additions 
        # unprocessed_start_pos = int(loc_info.split('x')[0])
        # unprocessed_end_pos = int(loc_info.split('x')[1])
        # if unprocessed_start_pos == unprocessed_end_pos:
        #    if unprocessed_start_pos == 0:
        #        return words[unprocessed_start_pos]
        #    else:
        #        return words[unprocessed_start_pos -1]

        raw_start, raw_end = map(int, loc_info.split('x')[:2])
        if raw_start == raw_end:
            return words[0 if raw_start == 0 else raw_start - 1]
        
        # Parse location information
        start_pos = int(loc_info.split('x')[0]) - 1  # Convert to 0-based index
        end_pos = int(loc_info.split('x')[1]) - 2    # Convert to 0-based index
        
        # Extract the lemma (inclusive of start_pos up to end_pos)
        lemma = ' '.join(words[start_pos:end_pos + 1])
        return lemma
    except (IndexError, ValueError) as e:
        print(f"Error extracting lemma for location {loc_info}: {e}", file=sys.stderr)
        return None

def process_apparatus(html_content):
    """
    Process the apparatus criticus and format variants with positive apparatus
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Define sigla and their order
    SIGLA_ORDER = ['C', 'Na', 'Nb', 'P', 'B', 'K', 'EdS', 'EdT']
    ALL_SIGLA = set(SIGLA_ORDER)
    
    def sort_sigla(sigla):
        """Sort sigla according to predefined order"""
        return sorted(sigla, key=lambda x: SIGLA_ORDER.index(x))
    
    # Get the main text content first
    maintext_div = soup.find('div', class_='maintext')
    maintext_content = ""
    if maintext_div:
        # Get all text nodes that are direct children (not within verselines)
        text_parts = []
        for content in maintext_div.children:
            if isinstance(content, str) and not isinstance(content, Comment):
                cleaned_text = content.strip()
                if cleaned_text:  # If there's any content after stripping
                    text_parts.append(cleaned_text)
        
        # Find all verselines
        verselines = maintext_div.find_all('div', class_='verseline')
        verse_texts = [line.get_text(strip=True) for line in verselines]
        
        # Combine all text parts with proper spacing
        all_parts = text_parts + verse_texts
        maintext_content = ' '.join(part for part in all_parts if part)
    
    # Group variants by lemma with their sigla
    variants = defaultdict(list)
    variant_sigla = defaultdict(set)  # Track which sigla appear in variants
    
    # Process each variant container
    for varcontainer in soup.find_all('span', class_='varcontainer'):
        try:
            loc_info = varcontainer.get('data-loc')
            if not loc_info:
                continue
                
            lemma = extract_lemma(maintext_content, loc_info)
            if not lemma:
                continue
            
            variant_span = varcontainer.find('span', class_='variant')
            if not variant_span:
                continue
            
            # Check if this is an addition
            editor_label = variant_span.find('span', class_='editor label')
            is_addition = editor_label and editor_label.get_text(strip=True).lower() == 'add'
            
            if is_addition:
                # Remove the 'add' label and get the actual addition text
                editor_label.decompose()
                variant_reading = variant_span.get_text(strip=True)
                variant_reading = f"ADD {variant_reading} {lemma}"
            else:
                variant_reading = variant_span.get_text(strip=True)
            
            # Find all manuscript sigla for this variant
            sigla = []
            for siglum_link in varcontainer.find_all('a', class_='msid'):
                siglum = siglum_link.get_text(strip=True)
                sigla.append(siglum)
            
            if not sigla:  # Skip if no sigla found
                continue
                
            # Store all sigla for this variant
            variants[lemma].append((variant_reading, sigla))
            variant_sigla[lemma].update(sigla)
            
        except Exception as e:
            print(f"Error processing variant: {e}", file=sys.stderr)
            continue
    
    # Format the variants with positive apparatus
    formatted_variants = []
    for lemma, readings in variants.items():
        # Find sigla that support the lemma (those not listed in variants)
        variant_mss = variant_sigla[lemma]
        lemma_sigla = ALL_SIGLA - variant_mss
        
        # Start building the apparatus entry
        variant_str = f"{lemma}] "
        
        # For additions, we don't need to show lemma witnesses
        if not any("ADD" in reading for reading, _ in readings):
            if len(variant_mss) == 1:
                # If only one manuscript has a variant, use Σ
                variant_str += "Σ"
            else:
                # Add the sigla that support the lemma in custom order
                variant_str += " ".join(sort_sigla(lemma_sigla))
        
        # Add the variants
        readings_str = []
        for reading, sigla in readings:
            # Join all sigla for this reading in custom order
            sigla_str = " ".join(sort_sigla(sigla))
            readings_str.append(f"{reading} {sigla_str}")
        
        formatted_variants.append(f"{variant_str}; {'; '.join(readings_str)}")
    
    return maintext_content, formatted_variants

def run_collation():
    """Run the collate.php script and process its output"""
    try:
        # Run the PHP script
        result = subprocess.run(['php', 'collate.php'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        # Process the apparatus and get both main text and variants
        maintext, formatted_variants = process_apparatus(result.stdout)
        
        # Print the main text
        print("\nMain text:")
        print(maintext)
        
        # Print the formatted variants
        print("\nApparatus criticus:")
        for variant in formatted_variants:
            print(variant)
        
        return formatted_variants
        
    except subprocess.CalledProcessError as e:
        print(f"Error running collate.php: {e}", file=sys.stderr)
        print(f"PHP script output: {e.output}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error processing collation output: {e}", file=sys.stderr)
        raise

# [Rest of the script remains the same]

# [Rest of the script remains the same]
def process_all_files(target_id):
    """Process all specified input files and run collation"""
    input_files = [
        'htec.txt',
        'htc.txt',
        'htna.txt',
        'htnb.txt',
        'htp.txt',
        'htb.txt',
        'htk.txt',
        'htes.txt',
        'htet.txt'
    ]
    
    success_count = 0
    for input_file in input_files:
        try:
            process_tei_file(input_file, target_id)
            success_count += 1
        except Exception as e:
            print(f"Failed to process {input_file}: {e}", file=sys.stderr)
            continue
    
    # print(f"\nProcessing complete. Successfully processed {success_count} out of {len(input_files)} files.")
    
    try:
        # print("\nRunning collation...")
        variants = run_collation()
        return variants
    except Exception as e:
        print(f"Failed to run collation: {e}", file=sys.stderr)
        return None

def main():
    """Main function to handle command line arguments and process all files"""
    if len(sys.argv) != 2:
        print("Usage: python script.py <xml:id>", file=sys.stderr)
        sys.exit(1)
    
    target_id = sys.argv[1]
    register_namespaces()
    process_all_files(target_id)

if __name__ == "__main__":
    main()
