# IMPORT ==========================================================
import xml.etree.ElementTree as ET
import pandas as pd

# CONST ==========================================================
# Don't forget to remove xmlns attribute from the DataCategoryGroup element
DATA_CATEGORIES_PATH = '/Users/macbook/Desktop/Import KB BBC/scripts Internal kb/Inputs/Internal.datacategorygroup-meta.xml'

# FUNCTIONS ==========================================================
def parse_category_group_xml_to_dataframe(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Initialize lists to store data
    rows = []
    
    # Function to recursively traverse XML elements
    def traverse_xml_data_categories(element, path):
        for child in element:
            if child.tag == 'dataCategory':
                newPath = path[:]
                newPath += [child.find('label').text, child.find('name').text]
                rows.append(newPath[:])  # Add a copy of the current path to rows
                traverse_xml_data_categories(child, newPath[:])
    def column_name(index):
        if index % 2 == 0:
            return f'label{index//2 +1}'
        return f'name{index//2 + 1}'
            
    # Start traversing from the root with an empty path
    for child in root:
        if child.tag == 'dataCategory':
            traverse_xml_data_categories(child, [])
    
    # Determine the maximum depth of hierarchy
    max_depth = max(len(row) for row in rows)
    
    # Create DataFrame with the desired column structure
    columns = [column_name(i) for i in range(max_depth)]
    df = pd.DataFrame(rows, columns=columns)

    return df

# ====================================================================

df = parse_category_group_xml_to_dataframe(DATA_CATEGORIES_PATH)

# Create CSV
df.to_csv('Inputs/internal_data_categories.csv',index=False)