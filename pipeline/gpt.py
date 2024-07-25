import os
import dspy
from dspy import Prediction
from openai.types.chat.completion_create_params import ResponseFormat

# Constants
MODELS_WITH_RESPONSE_FORMAT = [
    "ailab-llm"
]  # List of models that support the response_format option

class ProduceLabelForm(dspy.Signature):
    """
    You are a fertilizer label inspector working for the Canadian Food Inspection Agency. 
    Your task is to classify all information present in the provided text using the specified keys.
    Your response should be accurate, intelligible, formatted in JSON, and contain all the text from the provided text.
    """
    
    text = dspy.InputField(desc="The text of the fertilizer label extracted using OCR.")
    specification = dspy.InputField(desc="The specification containing the fields to highlight and their requirements.")
    form = dspy.OutputField(desc="Only a complete JSON.")

class GPT:
    def __init__(self, api_endpoint, api_key, deployment="ailab-gpt-35-turbo-16k"):
        if not api_endpoint or not api_key:
            raise ValueError("API endpoint and key are required to instantiate the GPT class.")

        # self.model = deployment

        response_format = None
        if deployment in MODELS_WITH_RESPONSE_FORMAT:
            response_format = ResponseFormat(type='json_object')

        max_token = 12000
        if deployment == 'ailab-llm':
            max_token = 3500


        self.dspy_client = dspy.AzureOpenAI(
            api_base=api_endpoint,
            api_key=api_key,
            deployment_id=deployment,
            api_version="2024-02-01",
            max_tokens=max_token,
            response_format=response_format,
        )

    def generate_form(self, prompt) -> Prediction:
        prompt_file = open(os.getenv("PROMPT_PATH"))
        system_prompt = prompt_file.read()
        prompt_file.close()

        dspy.configure(lm=self.dspy_client)
        signature = dspy.ChainOfThought(ProduceLabelForm)
        prediction = signature(specification=system_prompt, text=prompt)

        # print(prediction)
        return prediction
