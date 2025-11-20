from openai import OpenAI
client = OpenAI()  # usa tu API key en .env

def generate_explanation(shopping_list, total_cost):
    prompt = open("llm/prompts/explanation_prompt.txt").read()
    items_text = "\n".join([f"- {item['producto']} → {item['supermercado']} (${item['precio']:,.0f})" for item in shopping_list])
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": f"Lista:\n{items_text}\n\nCosto total: ${total_cost:,.0f}"}],
        temperature=0.7
    )
    return response.choices[0].message.content