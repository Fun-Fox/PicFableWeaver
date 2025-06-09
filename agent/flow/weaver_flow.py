
from pocketflow import Node, Flow

from agent.node.weaver_node import PicWeaverNode


class NoOp(Node):
    """Node that does nothing, used to properly end the flow."""
    pass


def weaver_flow(db_path):
    # Create nodes
    pic_weaver = PicWeaverNode()
    end = NoOp()
    # Connect nodes
    pic_weaver - "done" >> end
    # Create and run flow
    flow = Flow(start=pic_weaver)
    shared = {"db_path": db_path}
    flow.run(shared)