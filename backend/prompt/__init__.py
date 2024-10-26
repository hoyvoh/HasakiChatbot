'''
LLM + prompt specified by the query type

'''
from .awan_api import AwanAPI
from .prompt_design import PROMPT_TEMPLATE
import sys
sys.path.append("..")

__all__ = ['AwanAPI', 'PROMPT_TEMPLATE']
