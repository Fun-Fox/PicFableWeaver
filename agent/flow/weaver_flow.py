from pocketflow import Node, Flow

from agent.node.weaver_node import PicWeaverNode


class NoOp(Node):
    """Node that does nothing, used to properly end the flow."""
    pass


def weaver_flow(image_id_list, db_path):
    # Create nodes
    pic_weaver = PicWeaverNode()
    end = NoOp()
    # Connect nodes
    pic_weaver - "done" >> end
    # Create and run flow
    flow = Flow(start=pic_weaver)
    shared = {"image_id_list": image_id_list, "db_path": db_path}
    flow.run(shared)
