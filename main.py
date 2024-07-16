# IMPORTS ==========================================================
import pandas as pd
import os

# CONSTS ==========================================================
PATH_TO_INTERNAL_KB = '/Users/macbook/Desktop/Import KB BBC/scripts Internal kb/Inputs/internalKb.csv'
INTERNAL_KB_CSV_SEP = ';'
PATH_TO_DATA_CATEGORIES = 'Inputs/internal_data_categories.csv'
DATA_CATEGORIES_CSV_SEP = ','

RECORD_TYPE_ID = '012AP000001OkVl'

# IMPORT CSV FILES ==========================================================

internal_kb_df = pd.read_csv(PATH_TO_INTERNAL_KB, sep=INTERNAL_KB_CSV_SEP)
data_categories_df = pd.read_csv(PATH_TO_DATA_CATEGORIES, sep=DATA_CATEGORIES_CSV_SEP)

internal_kb_df = internal_kb_df.fillna('')
data_categories_df = data_categories_df.fillna('')

# FUNCTIONS ==========================================================

def format_language(language):
    if language:
        if '_' in language:
            language_split = language.split('_')
            language = language_split[0].lower() + '_' + language_split[1].upper()
        elif '-' in language:
            language_split = language.split('-')
            language = language_split[0].lower() + '_' + language_split[1].upper()
        else:
            language = language.lower()
        
        # Languages with different Salesforce code
        if language == 'pt':
            language = 'pt_PT'
        elif language == 'nl':
            language = 'nl_NL'
        elif language == 'sr':
            language = 'sh'
    
    return language

def map_data_category(category, section):
    result = { 'is_category_changed': False, 'category_name': '' }

    data_category_mapping = data_categories_df[
        (data_categories_df['label1'].str.lower() == category.lower()) &
        (data_categories_df['label3'].str.lower() == section.lower())
    ]

    if data_category_mapping.empty:
        data_category_mapping = data_categories_df[
            (data_categories_df['label1'].str.lower() == category.lower()) &
            (data_categories_df['label2'].str.lower() == section.lower()) &
            (data_categories_df['label3'].str.lower() == '')
        ]
    if data_category_mapping.empty:
        result['is_category_changed'] = True
        data_category_mapping = data_categories_df[
            (data_categories_df['label1'].str.lower() == category.lower()) &
            (data_categories_df['label2'].str.lower() == '') &
            (data_categories_df['label3'].str.lower() == '')
        ]  

    if not data_category_mapping.empty:
        mapping = data_category_mapping.iloc[0]
        if mapping['name3']:
            result['category_name'] = mapping['name3']
        elif mapping['name2']:
            result['category_name'] = mapping['name2']
        elif mapping['name1']:
            result['category_name'] = mapping['name1']

    return result

# ===============================================================================
# ============================== PROCESSING =====================================
# ===============================================================================
columns_internal_kb = ['id','IsMasterLanguage', 'Summary', 'Title', 'Language', 'Answer__c', 'RECORDTYPEID', 'category', 'section', 'attachment_url', 'attachment_url_nameless', 'attachment_name', 'attachment_inline']
columns_article = ['IsMasterLanguage', 'Summary', 'Title', 'Language', 'Answer__c', 'RecordTypeId', 'datacategorygroup.Internal', 'ZendeskId__c', 'ZendeskAttachmentUrlList__c', 'ZendeskAttachmentNameList__c', 'ZendeskIsAttachmentInlineList__c']
changed_internal_kb = pd.DataFrame(columns = columns_internal_kb)
articles_df = pd.DataFrame(columns = columns_article)

for index, row in internal_kb_df.iterrows():
    article_row = {}
    article_row['ZendeskId__c'] = row['id']
    article_row['IsMasterLanguage'] = row['IsMasterLanguage']
    article_row['Summary'] = row['Summary']
    article_row['Title'] = row['Title']
    article_row['Language'] = format_language(row['Language'])
    article_row['Answer__c'] = row['Answer__c']
    article_row['RecordTypeId'] = RECORD_TYPE_ID
    #article_row['ZendeskAttachmentUrlList__c'] =  row['attachment_url']
    article_row['ZendeskAttachmentNameList__c'] =  row['attachment_name']
    article_row['ZendeskIsAttachmentInlineList__c'] =  row['attachment_inline']
    if  row['IsMasterLanguage']:
        data_category_mapping_result = map_data_category(
            row['category'],
            row['section']
        )
        article_row['datacategorygroup.Internal'] = data_category_mapping_result['category_name']
        if data_category_mapping_result['is_category_changed']:
            changed_internal_kb.loc[len(changed_internal_kb)] = row

    articles_df.loc[len(articles_df)] = article_row


articles_df = articles_df.sort_values(by=['ZendeskId__c', 'IsMasterLanguage'], ascending=[True, False])

articles_df.to_csv(f'Outputs/import.csv',index=False)
changed_internal_kb.to_csv(f'Outputs/changed_internal_kb.csv',index=False)