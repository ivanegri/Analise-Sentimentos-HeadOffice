import json
import random

def generate_conversations(total_count=1000):
    """
    Gera conversas com 7 níveis de sentimento para testar nuances do modelo.
    Score esperado: 0-100
    """
    
    # Distribuição mais realista (maioria neutra/levemente positiva)
    counts = {
        "very_negative": int(total_count * 0.10),      # Score esperado: 0-15
        "negative": int(total_count * 0.15),           # Score esperado: 15-35
        "slightly_negative": int(total_count * 0.15),  # Score esperado: 35-45
        "neutral": int(total_count * 0.30),            # Score esperado: 45-55
        "slightly_positive": int(total_count * 0.15),  # Score esperado: 55-70
        "positive": int(total_count * 0.10),           # Score esperado: 70-85
        "very_positive": int(total_count * 0.05)       # Score esperado: 85-100
    }

    templates = {
        "very_negative": [
            "Você é um incompetente! Já falei que o {item} não funciona!",
            "Isso é um absurdo! Vou processar vocês pelo {item}.",
            "Equipe patética. Não sabem fazer nada direito com o {item}.",
            "Cala a boca e resolve o problema do {item}, já cansei!",
            "Seu serviço é uma porcaria completa. {item} horrível!",
        ],
        
        "negative": [
            "Estou muito insatisfeito com o {item}. Isso não deveria acontecer.",
            "Péssimo atendimento. O {item} continua com problema.",
            "Não é possível que o {item} atrase de novo. Muito ruim.",
            "Vocês prometeram resolver o {item} há semanas. Decepcionante.",
            "O {item} está completamente errado. Preciso de solução urgente.",
        ],
        
        "slightly_negative": [
            "O {item} não ficou como eu esperava, sinceramente.",
            "Achei que o {item} seria melhor. Um pouco decepcionado.",
            "O {item} demorou mais do que deveria, não é ideal.",
            "Esperava mais qualidade no {item}, mas tudo bem.",
            "O {item} tem alguns problemas que precisam ser ajustados.",
        ],
        
        "neutral": [
            "Recebi o {item}. Obrigado.",
            "Poderia informar o prazo do {item}?",
            "O {item} foi enviado conforme solicitado.",
            "Preciso de mais informações sobre o {item}.",
            "Vou verificar o {item} e retorno em breve.",
            "Confirmando recebimento do {item}.",
            "O {item} está em análise pela equipe.",
        ],
        
        "slightly_positive": [
            "O {item} atendeu o básico. Obrigado.",
            "Recebi o {item}, está ok. Valeu!",
            "O {item} chegou certinho. Agradeço.",
            "Gostei do {item}, dentro do esperado.",
            "O {item} resolveu meu problema. Bom trabalho.",
            "O atendimento foi adequado para o {item}.",
        ],
        
        "positive": [
            "Muito obrigado pelo {item}! Ficou ótimo.",
            "Adorei o {item}! Exatamente o que eu precisava.",
            "Excelente trabalho com o {item}. Parabéns!",
            "O {item} superou minhas expectativas. Muito bom!",
            "Estou muito satisfeito com o {item}. Obrigado!",
            "O {item} está perfeito! Vocês são muito competentes.",
        ],
        
        "very_positive": [
            "SENSACIONAL! O {item} ficou PERFEITO! Vocês são incríveis!",
            "Estou MUITO impressionado com o {item}! Excepcional! ⭐⭐⭐⭐⭐",
            "O {item} está MARAVILHOSO! Melhor impossível!",
            "Vocês são GÊNIOS! O {item} superou TODAS as expectativas!",
            "UAUUU! O {item} está IMPECÁVEL! Equipe nota 1000!",
        ]
    }

    # Itens e contextos variados para evitar repetição
    items = [
        "relatório", "projeto", "pedido", "código", "suporte", 
        "atendimento", "produto", "serviço", "orçamento", "proposta",
        "documento", "sistema", "aplicativo", "site", "plataforma",
        "entrega", "instalação", "configuração", "treinamento", "consultoria"
    ]

    dataset = []
    current_id = 1

    for sentiment, count in counts.items():
        for _ in range(count):
            msg_template = random.choice(templates[sentiment])
            
            # Substitui variável com item aleatório
            message = msg_template.format(item=random.choice(items))
            
            dataset.append({
                "id": current_id,
                "message": message,
                "sentiment": sentiment,
                "expected_score_range": get_expected_range(sentiment)
            })
            current_id += 1

    # Embaralha para teste cego
    random.shuffle(dataset)
    return dataset

def get_expected_range(sentiment):
    """Retorna faixa de score esperada para cada categoria"""
    ranges = {
        "very_negative": "0-15",
        "negative": "15-35",
        "slightly_negative": "35-45",
        "neutral": "45-55",
        "slightly_positive": "55-70",
        "positive": "70-85",
        "very_positive": "85-100"
    }
    return ranges.get(sentiment, "unknown")

# Gerar e salvar
data = generate_conversations(1000)
with open('conversas_whatsapp.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"✅ Sucesso! Arquivo 'conversas_whatsapp.json' gerado com {len(data)} conversas.")
print("\nDistribuição por categoria:")
from collections import Counter
dist = Counter([item['sentiment'] for item in data])
for sentiment, count in sorted(dist.items()):
    print(f"  • {sentiment}: {count} mensagens")