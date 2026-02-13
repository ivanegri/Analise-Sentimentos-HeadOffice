import json

file_path = '/home/ivan/Documentos/HeadOffice/Analise Sentimentos HeadOffice/Dry_Wash2.json'
target_id = '6983569e8f3e6bd8721cb4a4'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    found = False
    for conversation in data:
        if conversation.get('_id') == target_id:
            print(json.dumps(conversation, indent=2, ensure_ascii=False))
            found = True
            break
    
    if not found:
        print(f"Conversation with ID {target_id} not found.")

except Exception as e:
    print(f"Error: {e}")
