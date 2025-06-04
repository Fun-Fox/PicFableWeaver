---
base_model:
- meta-llama/Llama-3.1-8B-Instruct
- google/siglip2-so400m-patch14-384
tags:
- captioning
pipeline_tag: image-text-to-text
library_name: transformers
---
# Model Card for Llama JoyCaption Beta One

[Github](https://github.com/fpgaminer/joycaption)

JoyCaption is an image captioning Visual Language Model (VLM) built from the ground up as a free, open, and uncensored model for the community to use in training Diffusion models.

Key Features:
- **Free and Open**: Always released for free, open weights, no restrictions, and just like [bigASP](https://www.reddit.com/r/StableDiffusion/comments/1dbasvx/the_gory_details_of_finetuning_sdxl_for_30m/), will come with training scripts and lots of juicy details on how it gets built.
- **Uncensored**: Equal coverage of SFW and NSFW concepts. No "cylindrical shaped object with a white substance coming out on it" here.
- **Diversity**: All are welcome here. Do you like digital art? Photoreal? Anime? Furry? JoyCaption is for everyone. Pains are being taken to ensure broad coverage of image styles, content, ethnicity, gender, orientation, etc.
- **Minimal Filtering**: JoyCaption is trained on large swathes of images so that it can understand almost all aspects of our world. almost. Illegal content will never be tolerated in JoyCaption's training.


## Motivation

Automated descriptive captions enable the training and finetuning of diffusion models on a wider range of images, since trainers are no longer required to either find images with already associated text or write the descriptions themselves. They also improve the quality of generations produced by Text-to-Image models trained on them (ref: DALL-E 3 paper). But to-date, the community has been stuck with ChatGPT, which is expensive and heavily censored; or alternative models, like CogVLM, which are weaker than ChatGPT and have abysmal performance outside of the SFW domain.

I'm building JoyCaption to help fill this gap by performing near or on-par with GPT4o in captioning images, while being free, unrestricted, and open.


## How to Get Started with the Model

Please see the [Github](https://github.com/fpgaminer/joycaption) for more details.

Example usage:

```
import torch
from PIL import Image
from transformers import AutoProcessor, LlavaForConditionalGeneration


IMAGE_PATH = "image.jpg"
PROMPT = "Write a long descriptive caption for this image in a formal tone."
MODEL_NAME = "fancyfeast/llama-joycaption-beta-one-hf-llava"


# Load JoyCaption
# bfloat16 is the native dtype of the LLM used in JoyCaption (Llama 3.1)
# device_map=0 loads the model into the first GPU
processor = AutoProcessor.from_pretrained(MODEL_NAME)
llava_model = LlavaForConditionalGeneration.from_pretrained(MODEL_NAME, torch_dtype="bfloat16", device_map=0)
llava_model.eval()

with torch.no_grad():
	# Load image
	image = Image.open(IMAGE_PATH)

	# Build the conversation
	convo = [
		{
			"role": "system",
			"content": "You are a helpful image captioner.",
		},
		{
			"role": "user",
			"content": PROMPT,
		},
	]

	# Format the conversation
	# WARNING: HF's handling of chat's on Llava models is very fragile.  This specific combination of processor.apply_chat_template(), and processor() works
	# but if using other combinations always inspect the final input_ids to ensure they are correct.  Often times you will end up with multiple <bos> tokens
	# if not careful, which can make the model perform poorly.
	convo_string = processor.apply_chat_template(convo, tokenize = False, add_generation_prompt = True)
	assert isinstance(convo_string, str)

	# Process the inputs
	inputs = processor(text=[convo_string], images=[image], return_tensors="pt").to('cuda')
	inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)

	# Generate the captions
	generate_ids = llava_model.generate(
		**inputs,
		max_new_tokens=512,
		do_sample=True,
		suppress_tokens=None,
		use_cache=True,
		temperature=0.6,
		top_k=None,
		top_p=0.9,
	)[0]

	# Trim off the prompt
	generate_ids = generate_ids[inputs['input_ids'].shape[1]:]

	# Decode the caption
	caption = processor.tokenizer.decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
	caption = caption.strip()
	print(caption)
```


## vLLM

vLLM provides the highest performance inference for JoyCaption, and an OpenAI compatible API so JoyCaption can be used like any other VLMs.  Example usage:

```
vllm serve fancyfeast/llama-joycaption-beta-one-hf-llava --max-model-len 4096 --enable-prefix-caching
```

VLMs are a bit finicky on vLLM, and vLLM is memory hungry, so you may have to adjust settings for your particular environment, such as forcing eager mode, adjusting max-model-len, adjusting gpu_memory_utilization, etc.