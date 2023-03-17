import base64
import glob
import logging
import os
import textwrap
import uuid

from PIL import Image, ImageDraw, ImageFont

import openai

class StoryLord(object):

    def __init__(self, logger_name="storylord", openai_api_key=None):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)

        if openai_api_key is not None:
            openai.api_key = openai_api_key

    def create_story(self, story_prompt, artifact_directory):
        if not os.path.exists(f"{artifact_directory}/story.txt"):
            self.logger.info("Generating story")
            chat_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You are a storyteller."},
                    {"role": "user", "content": f"Write me a story about the following: {story_prompt}"},
                ]
            )

            story_text = chat_response["choices"][0]["message"]["content"]

            with open (f"{artifact_directory}/story.txt", "w") as f:
                f.write(story_text)
        else:
            self.logger.info("Story exists; skipping generation")
            with open (f"{artifact_directory}/story.txt", "r") as f:
                story_text = f.read()

        return story_text

    def create_image_captions(self, pages, artifact_directory):

        image_captions = []
        for i, page in enumerate(pages):
            filename = f"caption_{i:02d}.txt"
            if not os.path.exists(f"{artifact_directory}/{filename}"):
                self.logger.info(f"Generating caption {i:02d}")
                chat_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                        {"role": "system", "content": "You are an assistant."},
                        {"role": "user", "content": f'Write a single sentence image caption for this text: \"{page}\"'},
                    ]
                )

                caption = chat_response["choices"][0]["message"]["content"]
                with open (f"{artifact_directory}/{filename}", "w") as f:
                    f.write(caption)
            else:
                self.logger.info(f"Caption {i:02d} exists; skipping generation")
                with open (f"{artifact_directory}/{filename}", "r") as f:
                    caption = f.read()
            
            image_captions.append(caption)
        
        return image_captions

    def create_images(self, image_captions, artifact_directory):
        for i, caption in enumerate(image_captions):
            filename = f"img_{i:02d}.png"
            if not os.path.exists(f"{artifact_directory}/{filename}"):
                self.logger.info(f"Generating image {i:02d}")
                image_response = openai.Image.create(
                    prompt=caption,
                    n=1,
                    size="1024x1024",
                    response_format="b64_json"
                )["data"][0]

                with open(f"{artifact_directory}/{filename}", "wb") as f:
                    f.write(base64.b64decode(image_response['b64_json']))
            else:
                self.logger.info(f"Image {i:02d} exists; skipping generation")

    def create_pdf(self, pages, artifact_directory):
        image_files = [f.split("/")[-1] for f in sorted(glob.glob(f"{artifact_directory}/*.png"))]

        image_list = []
        # This needs proper sorting
        for i, (page_text, image_file) in enumerate(zip(pages, image_files)):
            
            image = Image.open(os.path.join(artifact_directory, image_file))
            new_image = Image.new('RGB', (1024, 1500), (256,256,256))
            new_image.paste(image, (0, 0))

            I1 = ImageDraw.Draw(new_image)
            font = ImageFont.truetype("Verdana", size=40)
            I1.text((30, 1024+30), "\n".join(textwrap.wrap(page_text, width=45)), fill=(0, 0, 0), font=font)

            #im = image.convert('RGB')
            image_list.append(new_image)

        im_0 = image_list.pop(0)    
        im_0.save(f'{artifact_directory}/storybook.pdf', save_all=True, append_images=image_list)
 
    def create_storybook(self, story_prompt, artifact_directory=None):

        # Set and create an artifact_directory if not specified
        if artifact_directory is None:
            artifact_directory = f"./tmp/{str(uuid.uuid4())}"
            if not os.path.exists(artifact_directory):
                os.makedirs(artifact_directory)
        
        # Create story
        story_text = self.create_story(story_prompt, artifact_directory)

        # Create image captions
        pages = [p for p in story_text.split("\n") if p != ""]
        image_captions = self.create_image_captions(pages, artifact_directory)

        # Create images
        self.create_images(image_captions, artifact_directory)

        # Create storybook
        self.create_pdf(pages, artifact_directory)