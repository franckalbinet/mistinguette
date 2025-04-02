# mistinguette


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

## Install

``` sh
pip install mistinguette
```

## Getting started

OpenAI’s Python SDK will automatically be installed with Cosette, if you
don’t already have it.

``` python
from mistinguette import *
```

Cosette only exports the symbols that are needed to use the library, so
you can use `import *` to import them. Alternatively, just use:

``` python
import mistinguette
```

…and then add the prefix `mistinguette.` to any usages of the module.

<!-- Cosette provides `models`, which is a list of models currently available from the SDK. -->

``` python
models
```

    ['codestral-2501',
     'mistral-large-2411',
     'pixtral-large-2411',
     'mistral-saba-2502',
     'ministral-3b-2410',
     'ministral-8b-2410',
     'mistral-embed-2312',
     'mistral-moderation-2411',
     'mistral-ocr-2503',
     'mistral-small-2503',
     'open-mistral-nemo-2407']

For these examples, we’ll use `mistral-large-2411`.

``` python
model = models[1]
```

## Chat

The main interface to Cosette is the
[`Chat`](https://franckalbinet.github.io/mistinguette/core.html#chat)
class, which provides a stateful interface to the models:

``` python
chat = Chat(model, sp="""You are a helpful and concise assistant.""")
chat("I'm Jeremy")
```

Hello Jeremy! Nice to meet you. How can I assist you today?

<details>

- id: 401b34940c76413b93fde428839d2f28
- object: chat.completion
- model: mistral-large-2411
- usage: prompt_tokens=18 completion_tokens=16 total_tokens=34
- created: 1743589362
- choices: \[ChatCompletionChoice(index=0,
  message=AssistantMessage(content=‘Hello Jeremy! Nice to meet you. How
  can I assist you today?’, tool_calls=None, prefix=False,
  role=‘assistant’), finish_reason=‘stop’)\]

</details>

``` python
r = chat("What's my name?")
r
```

Jeremy

<details>

- id: 851227e58cbe4e6b97751897578ec3e5
- object: chat.completion
- model: mistral-large-2411
- usage: prompt_tokens=50 completion_tokens=2 total_tokens=52
- created: 1743589366
- choices: \[ChatCompletionChoice(index=0,
  message=AssistantMessage(content=‘Jeremy’, tool_calls=None,
  prefix=False, role=‘assistant’), finish_reason=‘stop’)\]

</details>

As you see above, displaying the results of a call in a notebook shows
just the message contents, with the other details hidden behind a
collapsible section. Alternatively you can `print` the details:

``` python
print(r)
```

    id='851227e58cbe4e6b97751897578ec3e5' object='chat.completion' model='mistral-large-2411' usage=In: 50; Out: 2; Total: 52 created=1743589366 choices=[ChatCompletionChoice(index=0, message=AssistantMessage(content='Jeremy', tool_calls=None, prefix=False, role='assistant'), finish_reason='stop')]

You can use `stream=True` to stream the results as soon as they arrive
(although you will only see the gradual generation if you execute the
notebook yourself, of course!)

``` python
for o in chat("What's your name?", stream=True): print(o, end='')
```

    I don't have a name. I'm here to assist you. Is there something specific you would like help with?

## Model Capabilities

Different Mistral AI models have different capabilities. For instance,
`mistral-large-2411` can not take an image as input as opposed to
`pixtral-large-2411`:

``` python
# o1 does not support streaming or setting the temperature
m = "mistral-large-2411"
can_stream(m), can_set_system_prompt(m), can_set_temperature(m), can_use_image(m)
```

    (True, True, True, False)

## Tool use

[Tool use](https://docs.mistral.ai/capabilities/function_calling/) lets
the model use external tools.

We use [docments](https://fastcore.fast.ai/docments.html) to make
defining Python functions as ergonomic as possible. Each parameter (and
the return value) should have a type, and a docments comment with the
description of what it is. As an example we’ll write a simple function
that adds numbers together, and will tell us when it’s being called:

``` python
def sums(
    a:int,  # First thing to sum
    b:int=1 # Second thing to sum
) -> int: # The sum of the inputs
    "Adds a + b."
    print(f"Finding the sum of {a} and {b}")
    return a + b
```

Sometimes the model will say something like “according to the `sums`
tool the answer is” – generally we’d rather it just tells the user the
answer, so we can use a system prompt to help with this:

``` python
sp = "Never mention what tools you use."
```

We’ll get the model to add up some long numbers:

``` python
model
```

    'mistral-large-2411'

``` python
a,b = 604542,6458932
pr = f"What is {a}+{b}?"
pr
```

    'What is 604542+6458932?'

To use tools, pass a list of them to
[`Chat`](https://franckalbinet.github.io/mistinguette/core.html#chat):

``` python
chat = Chat(model, sp=sp, tools=[sums])
```

Now when we call that with our prompt, the model doesn’t return the
answer, but instead returns a `tool_use` message, which means we have to
call the named tool with the provided parameters:

``` python
r = chat(pr)
r
```

    Finding the sum of 604542 and 6458932

- id: add10a17e8494845a76595e45d765ba7
- object: chat.completion
- model: mistral-large-2411
- usage: prompt_tokens=132 completion_tokens=37 total_tokens=169
- created: 1743589453
- choices: \[ChatCompletionChoice(index=0,
  message=AssistantMessage(content=’‘,
  tool_calls=\[ToolCall(function=FunctionCall(name=’sums’,
  arguments=’{“a”: 604542, “b”: 6458932}’), id=’TLVUDh6Me’, type=None,
  index=0)\], prefix=False, role=’assistant’),
  finish_reason=‘tool_calls’)\]

Cosette handles all that for us – we just have to pass along the
message, and it all happens automatically:

``` python
chat()
```

What is 604542+6458932? The answer is 7,063,474.

<details>

- id: d4c05d5724fa433cb9020371edc15f97
- object: chat.completion
- model: mistral-large-2411
- usage: prompt_tokens=197 completion_tokens=33 total_tokens=230
- created: 1743589467
- choices: \[ChatCompletionChoice(index=0,
  message=AssistantMessage(content=‘What is 604542+6458932? The answer
  is 7,063,474.’, tool_calls=None, prefix=False, role=‘assistant’),
  finish_reason=‘stop’)\]

</details>

You can see how many tokens have been used at any time by checking the
`use` property.

``` python
chat.use
```

    In: 329; Out: 70; Total: 399

### Tool loop

We can do everything needed to use tools in a single step, by using
[`Chat.toolloop`](https://franckalbinet.github.io/mistinguette/toolloop.html#chat.toolloop).
This can even call multiple tools as needed solve a problem. For
example, let’s define a tool to handle multiplication:

``` python
def mults(
    a:int,  # First thing to multiply
    b:int=1 # Second thing to multiply
) -> int: # The product of the inputs
    "Multiplies a * b."
    print(f"Finding the product of {a} and {b}")
    return a * b
```

Now with a single call we can calculate `(a+b)*2` – by passing
`show_trace` we can see each response from the model in the process:

``` python
chat = Chat(model, sp=sp, tools=[sums,mults])
pr = f'Calculate ({a}+{b})*2'
pr
```

    'Calculate (604542+6458932)*2'

``` python
def pchoice(r): print(r.choices[0])
```

``` python
r = chat.toolloop(pr, trace_func=pchoice)
```

    Finding the sum of 604542 and 6458932
    Finding the product of 2 and 7103474
    Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_Sfet73hgfRtSI2N25K97D7tO', function=Function(arguments='{"a": 604542, "b": 6458932}', name='sums'), type='function'), ChatCompletionMessageToolCall(id='call_mFQNJgjATAI2pYFFQyvfg0W2', function=Function(arguments='{"a": 2, "b": 7103474}', name='mults'), type='function')]))
    Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='The result of \\((604542 + 6458932) \\times 2\\) is 14,206,948.', refusal=None, role='assistant', audio=None, function_call=None, tool_calls=None))

OpenAI uses special tags for math equations, which we can replace using
`wrap_latex`:

``` python
wrap_latex(contents(r))
```

The result of $(604542 + 6458932) \times 2$ is 14,206,948.

## Images

As everyone knows, when testing image APIs you have to use a cute puppy.

``` python
fn = Path('samples/puppy.jpg')
display.Image(filename=fn, width=200)
```

<img src="index_files/figure-commonmark/cell-23-output-1.jpeg"
width="200" />

We create a
[`Chat`](https://franckalbinet.github.io/mistinguette/core.html#chat)
object as before:

``` python
model = "pixtral-large-2411"
```

``` python
chat = Chat(model)
```

Mistinguette expects images as a list of bytes, so we read in the file:

``` python
img = fn.read_bytes()
```

Prompts to Claudia can be lists, containing text, images, or both, eg:

``` python
chat([img, "In brief, what color flowers are in this image?"])
```

The flowers in the image are purple. These purple flowers seem to be
daisy-like, and they are growing near the puppy, which is lying on the
grass.

<details>

- id: 110860448b5f443588a5288fbe72a807
- object: chat.completion
- model: pixtral-large-2411
- usage: prompt_tokens=274 completion_tokens=36 total_tokens=310
- created: 1743589622
- choices: \[ChatCompletionChoice(index=0,
  message=AssistantMessage(content=‘The flowers in the image are purple.
  These purple flowers seem to be daisy-like, and they are growing near
  the puppy, which is lying on the grass.’, tool_calls=None,
  prefix=False, role=‘assistant’), finish_reason=‘stop’)\]

</details>

The image is included as input tokens.

``` python
chat.use
```

    In: 274; Out: 36; Total: 310

Alternatively, Mistinguette supports creating a multi-stage chat with
separate image and text prompts. For instance, you can pass just the
image as the initial prompt (in which case the model will make some
general comments about what it sees), and then follow up with questions
in additional prompts:

``` python
chat = Chat(model)
chat(img)
```

This is an adorable puppy! It looks like a Cavalier King Charles
Spaniel, known for its friendly and affectionate nature. These dogs are
great companions and enjoy being around people. They have a gentle
temperament and are well-suited to indoor living. If you have any
specific questions about this breed or puppies in general, feel free to
ask!

<details>

- id: 47c88a7e27004d3c832a5dc8277f30a4
- object: chat.completion
- model: pixtral-large-2411
- usage: prompt_tokens=263 completion_tokens=76 total_tokens=339
- created: 1743589646
- choices: \[ChatCompletionChoice(index=0,
  message=AssistantMessage(content=‘This is an adorable puppy! It looks
  like a Cavalier King Charles Spaniel, known for its friendly and
  affectionate nature. These dogs are great companions and enjoy being
  around people. They have a gentle temperament and are well-suited to
  indoor living. If you have any specific questions about this breed or
  puppies in general, feel free to ask!’, tool_calls=None, prefix=False,
  role=‘assistant’), finish_reason=‘stop’)\]

</details>

``` python
chat('What direction is the puppy facing?')
```

The puppy is facing the camera, looking directly at it. This means it is
facing forward from the perspective of the viewer.

<details>

- id: 118c686b1af64f42b04ff506a7e3f694
- object: chat.completion
- model: pixtral-large-2411
- usage: prompt_tokens=350 completion_tokens=27 total_tokens=377
- created: 1743589654
- choices: \[ChatCompletionChoice(index=0,
  message=AssistantMessage(content=‘The puppy is facing the camera,
  looking directly at it. This means it is facing forward from the
  perspective of the viewer.’, tool_calls=None, prefix=False,
  role=‘assistant’), finish_reason=‘stop’)\]

</details>

``` python
chat('What color is it?')
```

The puppy is a Cavalier King Charles Spaniel with a Blenheim coloring.
This means it has a white coat with chestnut or reddish-brown markings,
particularly on the ears and parts of the face. The spot on the top of
its head is a characteristic feature of the Blenheim color pattern.

<details>

- id: 9e7c3903c05740a2845e8dca2307428c
- object: chat.completion
- model: pixtral-large-2411
- usage: prompt_tokens=385 completion_tokens=69 total_tokens=454
- created: 1743589657
- choices: \[ChatCompletionChoice(index=0,
  message=AssistantMessage(content=‘The puppy is a Cavalier King Charles
  Spaniel with a Blenheim coloring. This means it has a white coat with
  chestnut or reddish-brown markings, particularly on the ears and parts
  of the face. The spot on the top of its head is a characteristic
  feature of the Blenheim color pattern.’, tool_calls=None,
  prefix=False, role=‘assistant’), finish_reason=‘stop’)\]

</details>

Note that the image is passed in again for every input in the dialog, so
that number of input tokens increases quickly with this kind of chat.

``` python
chat.use
```

    In: 998; Out: 172; Total: 1170
