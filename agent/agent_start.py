import os

from agent.flow.image_caption_flow import caption_flow, weaver_flow

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # image_dir = os.path.join(root_dir, "example")
    # caption_flow(image_dir,  os.path.join(root_dir, 'db/image_database.db'))
    weaver_flow(os.path.join(root_dir, 'db/image_database.db'))
