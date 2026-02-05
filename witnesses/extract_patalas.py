import sys
from lxml import etree

def filter_kalpas_patalas(xml_root, target_kalpa, target_paṭala):
    for kalpa in xml_root.xpath('//tei:div[@type="kalpa"]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
        kalpa_number = kalpa.get('n')
        
        if kalpa_number != target_kalpa:
            parent = kalpa.getparent()
            parent.remove(kalpa)
        else:
            for paṭala in kalpa.xpath('.//tei:div[@type="paṭala"]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
                paṭala_number = paṭala.get('n')
                if paṭala_number != target_paṭala:
                    kalpa.remove(paṭala)

def main():
    # Check if the required number of arguments are passed
    if len(sys.argv) != 3:
        print("Usage: extract_patalas.py file patala")
        sys.exit(1)

    # Set up file-related variables
    mainfile = sys.argv[1]
    target = sys.argv[2]
    fileparts = mainfile.split(".")
    basefilename = fileparts[0].split("_")[0]
    outputfilename = "./output/heta_" + target + "/" + basefilename + "_" + target + ".txt"

    # Parse the XML document
    tree = etree.parse(mainfile)
    root = tree.getroot()

    # Specify the target kalpa and paṭala numbers you want to keep
    targetparts = target.split(".")
    target_kalpa = targetparts[0]
    target_paṭala = targetparts[1]


    # Call the filtering function
    filter_kalpas_patalas(root, target_kalpa, target_paṭala)

    # Save the modified XML to a new file
    tree.write(outputfilename, encoding='utf-8', xml_declaration=True, pretty_print=True)

if __name__ == "__main__":
    main()
