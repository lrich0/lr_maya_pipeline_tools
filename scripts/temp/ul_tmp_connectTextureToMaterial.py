# Extracted verbatim from shelf_Unlisted.mel
#   This button had NO label of its own — its label and annotation were both
#   the entire script body, so it showed up on the shelf as a generic python
#   icon with no name.
#
# NEEDS REVISITING:
#  - a one-off from a specific job: hardcoded material "AAA_CarMat" and
#    texture "sourceimages/AAA_CarSwatch_02.png"
#  - the reusable part is the place2dTexture -> file node wiring, which is
#    otherwise a tedious 20-line manual job. Generalise into
#    "connect a texture to the selected material's colour" taking the
#    material and image path as arguments.
#  - connects to "<material>.color" (a lambert/blinn attribute). Would need
#    the renderer-aware slot mapping (baseColor for aiStandardSurface,
#    diffuse_color for Redshift) that the main module needs anyway.
#  - Maya has `mc.shadingNode('file', asTexture=True, isColorManaged=True)`
#    and the `place2dTexture` connection set can be driven by a loop over
#    attribute name pairs rather than 20 explicit connectAttr calls

import maya.cmds as mc

# Define the material name and file path
material_name = "AAA_CarMat"
file_path = "sourceimages/AAA_CarSwatch_02.png"

# Check if the material exists
if not mc.objExists(material_name):
    mc.warning(f"Material '{material_name}' does not exist. Please create it first.")
else:
    # Create a file node
    file_node = mc.shadingNode('file', asTexture=True, name=f"{material_name}_File")

    # Set the image file path
    mc.setAttr(f"{file_node}.fileTextureName", file_path, type="string")

    # Create a place2dTexture node
    place2d_node = mc.shadingNode('place2dTexture', asUtility=True, name=f"{material_name}_Place2dTexture")

    # Connect the place2dTexture node to the file node
    mc.connectAttr(f"{place2d_node}.outUV", f"{file_node}.uvCoord")
    mc.connectAttr(f"{place2d_node}.outUvFilterSize", f"{file_node}.uvFilterSize")
    mc.connectAttr(f"{place2d_node}.vertexCameraOne", f"{file_node}.vertexCameraOne")
    mc.connectAttr(f"{place2d_node}.vertexUvOne", f"{file_node}.vertexUvOne")
    mc.connectAttr(f"{place2d_node}.vertexUvThree", f"{file_node}.vertexUvThree")
    mc.connectAttr(f"{place2d_node}.vertexUvTwo", f"{file_node}.vertexUvTwo")
    mc.connectAttr(f"{place2d_node}.coverage", f"{file_node}.coverage")
    mc.connectAttr(f"{place2d_node}.mirrorU", f"{file_node}.mirrorU")
    mc.connectAttr(f"{place2d_node}.mirrorV", f"{file_node}.mirrorV")
    mc.connectAttr(f"{place2d_node}.noiseU", f"{file_node}.noiseU")
    mc.connectAttr(f"{place2d_node}.noiseV", f"{file_node}.noiseV")
    mc.connectAttr(f"{place2d_node}.offsetU", f"{file_node}.offsetU")
    mc.connectAttr(f"{place2d_node}.offsetV", f"{file_node}.offsetV")
    mc.connectAttr(f"{place2d_node}.repeatU", f"{file_node}.repeatU")
    mc.connectAttr(f"{place2d_node}.repeatV", f"{file_node}.repeatV")
    mc.connectAttr(f"{place2d_node}.rotateFrame", f"{file_node}.rotateFrame")
    mc.connectAttr(f"{place2d_node}.rotateUV", f"{file_node}.rotateUV")
    mc.connectAttr(f"{place2d_node}.stagger", f"{file_node}.stagger")
    mc.connectAttr(f"{place2d_node}.translateFrame", f"{file_node}.translateFrame")
    mc.connectAttr(f"{place2d_node}.wrapU", f"{file_node}.wrapU")
    mc.connectAttr(f"{place2d_node}.wrapV", f"{file_node}.wrapV")

    # Connect the file node to the color attribute of the material
    mc.connectAttr(f"{file_node}.outColor", f"{material_name}.color")

    print(f"File node '{file_node}' created and connected to '{material_name}.color' with path '{file_path}'.")
