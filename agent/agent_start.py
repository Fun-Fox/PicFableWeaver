import os

from agent.flow.image_caption_flow import caption_flow

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    image_dir = os.path.join(current_dir, "example")
    caption_flow(image_dir)
