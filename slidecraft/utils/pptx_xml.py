
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def SubElement(parent, tagname, **kwargs):
    element = OxmlElement(tagname)
    element.attrib.update(kwargs)
    parent.append(element)
    return element

from pptx.oxml.ns import qn

def apply_text_shadow(run):
    """Apply a subtle shadow to text run."""
    r = run._r
    rPr = r.get_or_add_rPr()
    
    # Text Shadow (Outer Shadow)
    effectLst = rPr.find(qn('a:effectLst'))
    if effectLst is None:
        effectLst = OxmlElement('a:effectLst')
        rPr.append(effectLst)
    
    outerShdw = SubElement(effectLst, 'a:outerShdw', blurRad='57150', dist='95250', dir='2700000', algn='tl', rotWithShape='0')
    srgbClr = SubElement(outerShdw, 'a:srgbClr', val='000000')
    alpha = SubElement(srgbClr, 'a:alpha', val='43137')

def apply_soft_glow(shape, color_hex="38bdf8", alpha="40000"):
    """Apply a soft outer glow to a shape."""
    if shape.element.spPr is None:
        shape.fill.solid() # Force creation 
        
    spPr = shape.element.spPr
    effectLst = spPr.get_or_add_effectLst()
    glow = SubElement(effectLst, 'a:glow', rad="101600") # ~8pt
    srgbClr = SubElement(glow, 'a:srgbClr', val=color_hex.replace("#", ""))
    SubElement(srgbClr, 'a:alpha', val=alpha)

def apply_drop_shadow(shape, transparency=60, blur=8, distance=3, angle=45):
    """Apply a modern drop shadow to a shape."""
    if shape.element.spPr is None:
        shape.fill.solid()
        
    spPr = shape.element.spPr
    effectLst = spPr.get_or_add_effectLst()
    
    # Calculate values
    # blurRad: EMUs
    # dist: EMUs
    # dir: 60000ths of a degree (45 deg = 2700000)
    
    outerShdw = SubElement(effectLst, 'a:outerShdw', 
                           blurRad=str(int(blur * 12700)), 
                           dist=str(int(distance * 12700)), 
                           dir=str(int(angle * 60000)), 
                           algn='ctr', 
                           rotWithShape='0')
    
    srgbClr = SubElement(outerShdw, 'a:srgbClr', val='000000')
    alpha_val = int((100 - transparency) * 1000)
    SubElement(srgbClr, 'a:alpha', val=str(alpha_val))

def apply_gradient_fill(shape, color1_hex, color2_hex, direction='linear', angle=270):
    """Apply a linear gradient fill to a shape."""
    if shape.element.spPr is None:
        shape.fill.solid()
        
    spPr = shape.element.spPr
    
    # Remove existing fill
    existing_fill = spPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill")
    if existing_fill is not None:
        spPr.remove(existing_fill)
        
    gradFill = SubElement(spPr, 'a:gradFill', rotWithShape="1")
    
    gsLst = SubElement(gradFill, 'a:gsLst')
    
    # Gradient Stop 1 (0%)
    gs1 = SubElement(gsLst, 'a:gs', pos="0")
    srgbClr1 = SubElement(gs1, 'a:srgbClr', val=color1_hex.replace("#", ""))
    
    # Gradient Stop 2 (100%)
    gs2 = SubElement(gsLst, 'a:gs', pos="100000")
    srgbClr2 = SubElement(gs2, 'a:srgbClr', val=color2_hex.replace("#", ""))
    
    # Linear Shade properties
    lin = SubElement(gradFill, 'a:lin', ang=str(int(angle * 60000)), scaled="1")

def apply_reflection(shape):
    """Apply a bottom reflection."""
    if shape.element.spPr is None:
        shape.fill.solid()
        
    spPr = shape.element.spPr
    effectLst = spPr.get_or_add_effectLst()
    reflection = SubElement(effectLst, 'a:refln', 
                            blurRad='6350', 
                            stA='50000', 
                            endA='300', 
                            endPos='35000', 
                            dist='0', 
                            dir='5400000', 
                            sy='-100000', 
                            algn='bl', 
                            rotWithShape='0')
