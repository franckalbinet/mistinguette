# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['model_types', 'all_models', 'models', 'find_block', 'contents', 'usage', 'Client']

# %% ../nbs/00_core.ipynb 3
import os
from collections import abc
try: from IPython import display
except: display=None
from fastcore.utils import *
from rich import print
from msglm import mk_msg_openai as mk_msg, mk_msgs_openai as mk_msgs

from mistralai import Mistral
from mistralai.models import ChatCompletionChoice, ChatCompletionResponse, UsageInfo, CompletionEvent
from mistralai.types import BaseModel

# %% ../nbs/00_core.ipynb 6
model_types = {
    # Premier models
    'codestral-2501': 'codestral-latest', # code generation model
    'mistral-large-2411': 'mistral-large-latest', # top-tier reasoning model for high-complexity tasks
    'pixtral-large-2411': 'pixtral-large-latest', # frontier-class multimodal model
    'mistral-saba-2502': 'mistral-saba-latest', # model for languages from the Middle East and South Asia
    'ministral-3b-2410': 'ministral-3b-latest', # edge model
    'ministral-8b-2410': 'ministral-8b-latest', # edge model with high performance/price ratio
    'mistral-embed-2312': 'mistral-embed', # embedding model
    'mistral-moderation-2411': 'mistral-moderation-latest', # moderation service to detect harmful text content
    'mistral-ocr-2503': 'mistral-ocr-latest', # OCR model to extract interleaved text and images
    
    # Free models (with weight availability)
    'mistral-small-2503': 'mistral-small-latest', # small model with image understanding capabilities
    
    # Research models
    'open-mistral-nemo-2407': 'open-mistral-nemo', # multilingual open source model
}

all_models = list(model_types)

# %% ../nbs/00_core.ipynb 9
models = all_models

# %% ../nbs/00_core.ipynb 18
def find_block(r:abc.Mapping, # The message to look in
              ):
    "Find the message in `r`"
    if isinstance(r, CompletionEvent): r = r.data # if async
    m = nested_idx(r, 'choices', 0)
    if not m: return m
    if hasattr(m, 'message'): return m.message
    return m.delta

# %% ../nbs/00_core.ipynb 20
def contents(r):
    "Helper to get the contents from response `r`."
    blk = find_block(r)
    if not blk: return r
    if hasattr(blk, 'content'): return getattr(blk,'content')
    return blk

# %% ../nbs/00_core.ipynb 22
@patch
def _repr_markdown_(self:ChatCompletionResponse):
    det = '\n- '.join(f'{k}: {v}' for k,v in dict(self).items())
    res = contents(self)
    if not res: return f"- {det}"
    return f"""{contents(self)}

<details>

- {det}

</details>"""

# %% ../nbs/00_core.ipynb 25
def usage(inp=0, # input tokens
          out=0,  # Output tokens
         ):
    "Slightly more concise version of `UsageInfo`."
    return UsageInfo(prompt_tokens=inp, completion_tokens=out, total_tokens=inp+out)

# %% ../nbs/00_core.ipynb 27
@patch
def __repr__(self:UsageInfo): return f'In: {self.prompt_tokens}; Out: {self.completion_tokens}; Total: {self.total_tokens}'

# %% ../nbs/00_core.ipynb 29
@patch
def __add__(self:UsageInfo, b):
    "Add together each of `input_tokens` and `output_tokens`"
    return usage(self.prompt_tokens+b.prompt_tokens, self.completion_tokens+b.completion_tokens)

# %% ../nbs/00_core.ipynb 32
@patch(as_prop=True)
def total(self:UsageInfo): return self.total_tokens

# %% ../nbs/00_core.ipynb 44
class Client:
    def __init__(self, model, cli=None):
        "Basic LLM messages client."
        self.model,self.use = model,usage(0,0)
        # self.text_only = model in text_only_models
        self.c = (cli or Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))).chat.complete
