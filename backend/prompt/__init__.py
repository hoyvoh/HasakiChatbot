'''
LLM + prompt specified by the query type

'''
# from .awan_api import AwanAPI
from .openai_api import OpenAIClient
from .prompt_design import PROMPT_TEMPLATE

import sys
sys.path.append("..")

__all__ = ['PROMPT_TEMPLATE', 'OpenAIClient']
