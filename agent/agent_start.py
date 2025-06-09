import os

from agent.flow.caption_flow import caption_flow
from agent.flow.weaver_flow import weaver_flow

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    db_path = os.path.join(root_dir, 'db/image_database.db')
    image_dir = os.path.join(root_dir, "example")
    caption_flow(image_dir, db_path)
    weaver_flow(image_id_list=[], db_path=db_path)
