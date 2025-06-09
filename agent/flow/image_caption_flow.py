from pocketflow import Node, Flow

from agent.node.caption_node import ImageCaptionNode
from agent.node.weaver_node import PicWeaverNode


class NoOp(Node):
    """Node that does nothing, used to properly end the flow."""
    pass


def caption_flow(image_dir):
    # Create nodes
    image_caption = ImageCaptionNode()
    pic_weaver = PicWeaverNode()
    end = NoOp()
    # Connect nodes
    image_caption - "desc" >> pic_weaver
    # Create and run flow
    flow = Flow(start=image_caption)
    shared = {"image_dir": image_dir}
    flow.run(shared)



