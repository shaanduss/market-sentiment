# Project Description

This script goes through Financial News Headlines and classifies them into "negative", "neutral" or "positive".

## Steps (current)

1. Connect to SambaNova.AI Client
2. Generate the model system context.
3. Currently, the list of headlines is a static array.
4. Creates the list of models to be used.
5. Goes through each headline and passes it through each selected model.
6. Stores the response for each model. With each response being in the format:
   "<label>, <confidence_score>"
7. Flags any labels with a score below 0.6 confidence
8. Outputs the results for each headline and model rating.

## Example Output for One Headline

- Headline Passed: blackrock pulling bitcoin whales wall street orbit
- Llama 3.3 70B Label: positive
- Llama 3.3 70B Confidence Score: 0.70
- Llama 3.1 8B Label: negative
- Llama 3.1 8B Confidence Score: 0.85
- DeepSeek R1 Label: positive
- DeepSeek R1 Confidence Score: 0.85

# Future Extensions

1. Scrape Headlines from Yahoo Finance using Selenium and creating a suitable data pipeline for that data. (Possibly a WebSocket/Scheduled Tasks).
2. Store processed headlines in a database with their corresponding confidence scores.
3. Generate a mean label based on the 3 models' responses.
