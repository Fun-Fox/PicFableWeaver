from pocketflow import Node, Flow

from agent.node.caption_node import ImageCaptionNode


class NoOp(Node):
    """Node that does nothing, used to properly end the flow."""
    pass


if __name__ == "__main__":
    image_dir = ""
    # Create nodes
    image_caption = ImageCaptionNode()
    end = NoOp()

    # Connect nodes
    image_caption - "desc" >> end

    # Create and run flow
    flow = Flow(start=image_caption)
    shared = {"image_dir": image_dir}
    flow.run(shared)
