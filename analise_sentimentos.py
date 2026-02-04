import json
from textblob import TextBlob

path = 'headoffice_ai_exported_data_2026-01-29T12_42_59.262Z.json'
with open(path,'r',encoding='utf-8') as f:
    data1 = json.load(f)

path2 = 'headoffice_ai_exported_data_2026-01-29T12_57_37.700Z.json'
with open(path2,'r',encoding='utf-8') as f:
    data2 = json.load(f)

def conv_sentiment(conv):
    texts = []
    for m in conv.get('Full Conversation',[]):
        if not m.get('sender'):
            msg = m.get('message','').strip()
            if msg:
                texts.append(msg)
    if not texts:
        return 50.0
    text = '\n'.join(texts)
    pol = TextBlob(text).sentiment.polarity
    score = (pol + 1) * 50
    return max(0,min(100,score))

results = []
for d in data1+data2:
    s = conv_sentiment(d)
    cid = d.get('_id')
    results.append({'id':cid,'score':round(s,1)})

# cluster counts
c1 = sum(1 for r in results if r['score']<50)
c2 = sum(1 for r in results if 50<=r['score']<=75)
c3 = sum(1 for r in results if r['score']>75)
len(results), c1, c2, c3, results[:10]