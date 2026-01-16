import re

def remove_irrelevant_products(df, keywords_must_include):
    pattern = '|'.join(keywords_must_include)
    return df[df['product_name'].str.lower().str.contains(pattern, regex=True)]

def drop_duplicates(df):
    return df.drop_duplicates(subset='product_url')

def clean_weight(text):
    match = re.search(r'(\d+[.,]?\d*)\s?(kg|g|gram|gr|ml|l|liter)', text.lower())
    if match:
        val = float(match.group(1).replace(',', '.'))
        unit = match.group(2)
        if unit in ['g', 'gram', 'gr']:
            return val / 1000  # gram to kg
        elif unit in ['ml']:
            return val / 1000  # ml to liter
        elif unit in ['l', 'liter']:
            return val
        else:
            return val
    return None
