import json
import configparser
import sys


def parse_excalidraw_to_manim(input_file, output_file, manim_config_path="manim.cfg"):
    """Parse an Excalidraw .json file and generate a Manim script with dynamic scaling for frames."""

    # Step 1: Read Manim configuration
    config = configparser.ConfigParser()
    config.read(manim_config_path)

    # Get Manim screen dimensions
    manim_frame_width = 14  # Default 14 units
    manim_frame_height = 8  # Default 8 units
    if config.has_section("CLI"):
        manim_frame_width = float(config["CLI"].get(
            "frame_width", manim_frame_width))
        manim_frame_height = float(config["CLI"].get(
            "frame_height", manim_frame_height))

    with open(input_file, 'r') as file:
        excalidraw_data = json.load(file)

    shapes = excalidraw_data.get("elements", [])
    if not shapes:
        print("No elements found in the Excalidraw file.")
        return

    # Step 2: Aggregate objects into frames
    frames = {}
    for shape in shapes:
        frame_id = shape.get("frameId")
        if frame_id is not None:
            if frame_id not in frames:
                # find frame
                frame = next(
                    shape for shape in shapes if shape.get("id") == frame_id)
                frames[frame_id] = {
                    "width": frame.get("width"),
                    "height": frame.get("height"),
                    "x": frame.get("x"),
                    "y": frame.get("y"),
                    "name": frame.get("name"),
                    "objects": [],
                }
            object = {
                "type": shape.get("type"),
                "x": shape.get("x"),
                "y": shape.get("y"),
                "width": shape.get("width", 0),
                "height": shape.get("height", 0),
                "text": shape.get("text", ""),
                "fontSize": shape.get("fontSize", 0),
            }
            frames[frame_id]["objects"].append(object)

    # Step 3: Generate Manim scenes for each frame
    with open(output_file, 'w') as manim_file:
        manim_file.write("from manim import *\n\n")

        for frame_id, frame in frames.items():
            # Calculate scaling factor for the frame to fit Manim canvas
            frame_width = frame["width"]
            frame_height = frame["height"]
            frame_name = frame["name"]
            frame_x = frame["x"]
            frame_y = frame["y"]

            scale_x = manim_frame_width / frame_width
            scale_y = manim_frame_height / frame_height
            scale = min(scale_x, scale_y)  # Uniform scaling

            # log these data
            print(
                f"Frame{''.join(x for x in frame_name.title() if not x.isspace())}Scene:\n")
            print(f"  - Frame width: {frame_width}")
            print(f"  - Frame height: {frame_height}")
            print(f"  - Frame x: {frame_x}")
            print(f"  - Frame y: {frame_y}")
            print(f"  - Scale: {scale}")

            manim_file.write(
                f"class Frame{''.join(x for x in frame_name.title() if not x.isspace())}Scene(Scene):\n")
            manim_file.write("    def construct(self):\n")

            # manim_file.write(f"        # Frame scaling and centering\n")
            # manim_file.write(
            #     f"        frame_rect = Rectangle(width={frame_width * scale}, height={frame_height * scale}, color=BLUE)\n"
            # )
            # manim_file.write("        self.add(frame_rect)\n")

            # Scale and reposition objects inside the frame
            for obj in frame["objects"]:
                obj_x = (obj["x"] - frame_x - frame_width /
                         2 + obj["width"]/2) * scale
                obj_y = -(obj["y"] - frame_y - frame_height /
                          2 + obj["height"]/2) * scale
                obj_width = obj["width"] * scale
                obj_height = obj["height"] * scale

                # log these data
                # print(f"  - {obj['type']} at ({obj_x}, {obj_y})")

                if obj["type"] == "rectangle":
                    manim_file.write(
                        f"        self.add(Rectangle(width={obj_width}, height={obj_height}).move_to([{obj_x}, {obj_y}, 0]))\n"
                    )
                elif obj["type"] == "ellipse":
                    manim_file.write(
                        f"        self.add(Ellipse(width={obj_width}, height={obj_height}).move_to([{obj_x}, {obj_y}, 0]))\n"
                    )
                elif obj["type"] == "text":
                    text_lines = obj["text"].split("\n")
                    font_size = obj["fontSize"] * 0.3
                    manim_file.write(
                        f"        self.add(VGroup({', '.join([f'Text({repr(line)}, should_center=False, font_size={font_size})' for line in text_lines])}).arrange(DOWN, buff=0.02, center=False, aligned_edge=LEFT).move_to([{obj_x}, {obj_y}, 0]))\n"
                    )
                # Add support for other shapes as needed

            manim_file.write("\n")

    print(f"Manim script generated and saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 excalidraw-to-manim.py <input.excalidraw> <output.py>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    manim_config_path = "manim.cfg"  # Default config path
    if len(sys.argv) > 3:
        manim_config_path = sys.argv[3]

    parse_excalidraw_to_manim(input_file, output_file, manim_config_path)
