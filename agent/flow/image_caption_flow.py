
from pocketflow import Node, Flow

from agent.node.caption_node import ImageCaptionNode, ImageDescStructNode
from agent.node.weaver_node import PicWeaverNode

def caption_flow(image_dir,db_path):
    # Create nodes
    image_caption = ImageCaptionNode()
    image_desc_struct = ImageDescStructNode()
    pic_weaver = PicWeaverNode()
    # Connect nodes
    image_caption - "finish" >> image_desc_struct
    image_desc_struct - "finish" >> pic_weaver
    # Create and run flow
    flow = Flow(start=image_caption)
    shared = {"image_dir": image_dir, "db_path":db_path }
    flow.run(shared)



