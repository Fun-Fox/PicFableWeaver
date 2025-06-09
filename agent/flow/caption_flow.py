
from pocketflow import Node, Flow

from agent.node.caption_node import ImageCaptionNode, ImageDescStructNode

def caption_flow(image_dir,db_path):
    # Create nodes
    image_caption = ImageCaptionNode()
    image_desc_struct = ImageDescStructNode()
    # Connect nodes
    image_caption - "finish" >> image_desc_struct
    # Create and run flow
    flow = Flow(start=image_caption)
    shared = {"image_dir": image_dir, "db_path":db_path }
    flow.run(shared)



