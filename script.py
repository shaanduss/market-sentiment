from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import nltk
import os
from dotenv import load_dotenv
from sambanova import SambaNova

nltk.download('stopwords')
nltk.download('punkt')

stop_words = set(stopwords.words('english'))

def remove_stop_words(text):
  words = word_tokenize(text.lower())  # Tokenize and lower case
  filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
  return ' '.join(filtered_words)

def extract_sentiment_confidence(deepseek_response):
  # Remove reasoning enclosed in <think> tags
  if "<think>" in deepseek_response and "</think>" in deepseek_response:
    deepseek_response = deepseek_response.split("</think>")[-1].strip()

  # Match sentiment and confidence pattern
  match = re.search(r'(negative|neutral|positive),\s*(0?\.\d+|1(\.0+)?)', deepseek_response, re.IGNORECASE)
  if match:
    sentiment = match.group(1).lower()
    confidence = float(match.group(2))
    res = sentiment + ", " + str(confidence)
    return res
  else:
    # fallback if no match found
    return "neutral, 0.5"


headlines = [
  "GM stock jumps on upbeat full-year guidance as tariff exposure improves in Q3",
  "Coca-Cola stock pops as earnings top estimates amid 'challenging' environment",
  "BlackRock Is Pulling Bitcoin Whales Into Wall Street's Orbit",
  "Rare earths mining is having a crypto moment",
  "'Widow-Maker' Trade Becomes World Beater as Japan Bonds Sink",
  "Netflix stock falls after earnings miss estimates, operating profit takes a hit",
  "Tesla Q3 preview: Robotaxi, AI ambitions on the agenda following high-water mark in sales",
  "Capital One Announces $16 Billion Buyback as Profit Soars"
]

clean_headlines = []
for headline in headlines:
    clean_headlines.append(remove_stop_words(headline))

# Get API Key
load_dotenv()
api_key = os.getenv('SAMBANOVA_API_KEY')

client = SambaNova(
  api_key=api_key,
  base_url="https://api.sambanova.ai/v1",
)

model_context = """
You will be given financial news headlines.
Classify the sentiment as one of: negative, neutral, or positive.
Return ONLY: "<sentiment>, <confidence-score>"
Where <sentiment> is negative, neutral, or positive,
and <confidence-score> is a decimal number between 0 and 1 indicating your confidence.
Be critical and base decisions on keywords and phrases carefully.

Examples:
Text: "Earnings beat expectations despite tough market conditions."
Sentiment, Confidence: positive, 0.85
Text: "Company faces regulatory challenges with uncertain outlook."
Sentiment, Confidence: negative, 0.90
Text: "Stock price remains unchanged amid mixed signals."
Sentiment, Confidence: neutral, 0.75
Text: "Bitcoin surges as traders become optimistic."
Sentiment, Confidence: positive, 0.95
Text: "Economic slowdown concerns linger for investors."
Sentiment, Confidence: negative, 0.80

Text: "{input_text}"
Sentiment, Confidence:
"""

response_data = []
models = [
  "Meta-Llama-3.3-70B-Instruct",
  "Meta-Llama-3.1-8B-Instruct",
  "DeepSeek-R1-0528"
]
model_names = ["Llama 3.3 70B", "Llama 3.1 8B", "DeepSeek R1"]

for headline in clean_headlines:
  response_per_model = []

  for model in models:
    response = client.chat.completions.create(
      model=model,
      messages=[{"role":"system","content":model_context}, {"role":"user","content": headline}],
      temperature=0.1,
      top_p=0.1
    )
    # response_per_model = "<label>, <score>"

    processed_response = ""
    if (model != "DeepSeek-R1-0528"):
      processed_response = response.choices[0].message.content
    else:
      deepseek_response = extract_sentiment_confidence(response.choices[0].message.content)
      processed_response = deepseek_response

    response_per_model.append(processed_response.split(","))

  response_data.append(response_per_model)


for i in range(0, len(clean_headlines)):
  for j in range(0, len(models)):
    # Flag any labels with a confidence score < 60%
    if (float(response_data[i][j][1]) < 0.6):
      response_data[i][j][1] += " - BELOW THRESHOLD"

for i in range(0, len(clean_headlines)):
  print("Headline Passed: " + clean_headlines[i])
  for j in range(0, len(models)):
    print(model_names[j] + " Label: " + response_data[i][j][0])
    print(model_names[j] + " Confidence Score: " + response_data[i][j][1])
  print("------------")
