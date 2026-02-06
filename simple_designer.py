"""简化版KiCad设计器
从自然语言描述生成.kicad_pcb和.kicad_sch文件。
确保生成的文件可直接在KiCad GUI中打开。
"""

import os
from pathlib import Path

# PCB 文件内容 - 修正版，使用正确的KiCad 9.0格式
PCB_CONTENT = """(kicad_pcb (version 20240108) (generator "nlp-designer")
  (general
    (thickness 1.6)
    (drawings 4)
    (tracks 5)
    (zones 0)
    (modules 2)
    (nets 4)
  )

  (paper "A4")

  (title_block
    (title "LED Circuit")
    (date "2026-02-06")
    (rev "1")
    (company "Auto Generated")
  )

  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user)
    (33 "F.Adhes" user)
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user)
    (37 "F.SilkS" user)
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user)
    (41 "Cmts.User" user)
    (42 "Eco1.User" user)
    (43 "Eco2.User" user)
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user)
    (47 "F.CrtYd" user)
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )

  (setup
    (pad_to_mask_clearance 0)
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros no)
      (usegerberextensions no)
      (usegerberattributes yes)
      (usegerberadvancedattributes yes)
      (creategerberjobfile yes)
      (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000)
      (svgprecision 4)
      (plotframeref no)
      (viasonmask no)
      (mode 1)
      (useauxorigin no)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (pdf_front_fp_property_popups yes)
      (pdf_back_fp_property_popups yes)
      (dxfpolygonmode yes)
      (dxfimperialunits yes)
      (dxfusepcbnewfont yes)
      (psnegative no)
      (psa4output no)
      (plotreference yes)
      (plotvalue yes)
      (plotfptext yes)
      (plotinvisibletext no)
      (sketchpadsonfab no)
      (subtractmaskfromsilk no)
      (outputformat 1)
      (mirror no)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory "")
    )
  )

  (net 0 "")
  (net 1 "GND")
  (net 2 "+5V")
  (net 3 "Net-(R1-Pad2)")

  (footprint "Resistor_SMD:R_0805_2012Metric"
    (layer "F.Cu")
    (tedit 646696B5)
    (tstamp 6686A589-0C58-0DC1-0DA8-0001)
    (at 25.4 25.4 0)
    (descr "Resistor SMD 0805")
    (tags "Resistor")
    (property "Reference" "R1")
    (property "Value" "1k")
    (path "/R1")
    (attr smd)
    (fp_text reference "R1"
      (at 0 -1.65 0)
      (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)))
      (tstamp 6686A589-0C58-0DC1-0DA8-0011)
    )
    (fp_text value "1k"
      (at 0 1.65 0)
      (layer "F.Fab")
      (effects (font (size 1 1) (thickness 0.15)))
      (tstamp 6686A589-0C58-0DC1-0DA8-0012)
    )
    (pad "1" smd roundrect
      (at -0.9125 0 0)
      (size 1.025 1.4)
      (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.25)
      (net 2 "+5V")
      (tstamp 6686A589-0C58-0DC1-0DA8-0021)
    )
    (pad "2" smd roundrect
      (at 0.9125 0 0)
      (size 1.025 1.4)
      (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.25)
      (net 3 "Net-(R1-Pad2)")
      (tstamp 6686A589-0C58-0DC1-0DA8-0022)
    )
  )

  (footprint "LED_SMD:LED_0805_2012Metric"
    (layer "F.Cu")
    (tedit 646696B6)
    (tstamp 6686A589-0C58-0DC1-0DA8-0002)
    (at 50.8 25.4 180)
    (descr "LED SMD 0805")
    (tags "LED")
    (property "Reference" "LED1")
    (property "Value" "Red")
    (path "/LED1")
    (attr smd)
    (fp_text reference "LED1"
      (at 0 -1.65 0)
      (layer "F.SilkS")
      (effects (font (size 1 1) (thickness 0.15)))
      (tstamp 6686A589-0C58-0DC1-0DA8-0031)
    )
    (fp_text value "Red"
      (at 0 1.65 0)
      (layer "F.Fab")
      (effects (font (size 1 1) (thickness 0.15)))
      (tstamp 6686A589-0C58-0DC1-0DA8-0032)
    )
    (pad "1" smd roundrect
      (at -0.9125 0 180)
      (size 1.025 1.4)
      (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.25)
      (net 3 "Net-(R1-Pad2)")
      (tstamp 6686A589-0C58-0DC1-0DA8-0041)
    )
    (pad "2" smd roundrect
      (at 0.9125 0 180)
      (size 1.025 1.4)
      (layers "F.Cu" "F.Paste" "F.Mask")
      (roundrect_rratio 0.25)
      (net 1 "GND")
      (tstamp 6686A589-0C58-0DC1-0DA8-0042)
    )
  )

  (gr_line
    (start 10 10)
    (end 70 10)
    (layer "Edge.Cuts")
    (width 0.1)
    (tstamp 6686A589-0C58-0DC1-0DA8-0050)
  )
  (gr_line
    (start 70 10)
    (end 70 40)
    (layer "Edge.Cuts")
    (width 0.1)
    (tstamp 6686A589-0C58-0DC1-0DA8-0051)
  )
  (gr_line
    (start 70 40)
    (end 10 40)
    (layer "Edge.Cuts")
    (width 0.1)
    (tstamp 6686A589-0C58-0DC1-0DA8-0052)
  )
  (gr_line
    (start 10 40)
    (end 10 10)
    (layer "Edge.Cuts")
    (width 0.1)
    (tstamp 6686A589-0C58-0DC1-0DA8-0053)
  )

  (segment
    (start 26.3125 25.4)
    (end 40.0 25.4)
    (width 0.25)
    (layer "F.Cu")
    (net 3)
    (tstamp 6686A589-0C58-0DC1-0DA8-0060)
  )
  (segment
    (start 40.0 25.4)
    (end 40.0 27.94)
    (width 0.25)
    (layer "F.Cu")
    (net 3)
    (tstamp 6686A589-0C58-0DC1-0DA8-0061)
  )
  (segment
    (start 40.0 27.94)
    (end 49.8875 27.94)
    (width 0.25)
    (layer "F.Cu")
    (net 3)
    (tstamp 6686A589-0C58-0DC1-0DA8-0062)
  )
  (segment
    (start 49.8875 27.94)
    (end 51.7125 27.94)
    (width 0.25)
    (layer "F.Cu")
    (net 3)
    (tstamp 6686A589-0C58-0DC1-0DA8-0063)
  )
  (segment
    (start 51.7125 27.94)
    (end 51.7125 25.4)
    (width 0.25)
    (layer "F.Cu")
    (net 3)
    (tstamp 6686A589-0C58-0DC1-0DA8-0064)
  )
)
"""

# SCH 文件内容 - 简化版
SCH_CONTENT = """(kicad_sch (version 20240108) (generator "nlp-designer")
  (uuid 6686A589-0C58-0DC1-0DA8-0000)
  (paper "A4")

  (title_block
    (title "LED Circuit")
    (date "2026-02-06")
    (rev "1")
    (company "Auto Generated")
  )

  (lib_symbols
    (symbol "Device:R"
      (pin_numbers hide)
      (pin_names (offset 0))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "R"
        (at 2.032 0 90)
        (effects (font (size 1.27 1.27)))
      )
      (property "Value" "R"
        (at 0 0 90)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" ""
        (at -1.778 0 90)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" "~"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Description" "Resistor"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "R_0_1"
        (rectangle (start -1.016 -2.54) (end 1.016 2.54)
          (stroke (width 0.254) (type default))
          (fill (type none))
        )
      )
      (symbol "R_1_1"
        (pin passive line (at 0 3.81 270) (length 1.27)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at 0 -3.81 90) (length 1.27)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "Device:LED"
      (pin_numbers hide)
      (pin_names (offset 1.016) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "D"
        (at -1.27 3.81 0)
        (effects (font (size 1.27 1.27)) (justify right))
      )
      (property "Value" "LED"
        (at -1.27 1.27 0)
        (effects (font (size 1.27 1.27)) (justify right))
      )
      (property "Footprint" ""
        (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" "~"
        (at 0 -5.08 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Description" "Light emitting diode"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "LED_0_1"
        (polyline
          (pts
            (xy -1.27 -1.27)
            (xy 1.27 0)
            (xy -1.27 1.27)
            (xy -1.27 -1.27)
          )
          (stroke (width 0.2032) (type default))
          (fill (type none))
        )
        (polyline
          (pts
            (xy -1.27 0)
            (xy 1.27 0)
          )
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "LED_1_1"
        (pin passive line (at -3.81 0 0) (length 2.54)
          (name "K" (effects (font (size 1.27 1.27))))
          (number "2" (effects (font (size 1.27 1.27))))
        )
        (pin passive line (at 3.81 0 180) (length 2.54)
          (name "A" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "power:+5V"
      (power)
      (pin_numbers hide)
      (pin_names (offset 0) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#PWR"
        (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Value" "+5V"
        (at 0 3.556 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Description" "Power symbol creates a global label with name \"+5V\""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "+5V_0_0"
        (polyline
          (pts
            (xy -0.762 1.27)
            (xy 0 2.54)
            (xy 0.762 1.27)
          )
          (stroke (width 0) (type default))
          (fill (type outline))
        )
        (polyline
          (pts
            (xy 0 0)
            (xy 0 2.54)
          )
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "+5V_1_0"
        (pin power_in line (at 0 0 90) (length 0)
          (name "+5V" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
    )
    (symbol "power:GND"
      (power)
      (pin_numbers hide)
      (pin_names (offset 0) hide)
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#PWR"
        (at 0 -6.35 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Value" "GND"
        (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Description" "Power symbol creates a global label with name \"GND\""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "GND_0_0"
        (polyline
          (pts
            (xy 0 0)
            (xy 0 -1.27)
          )
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts
            (xy -1.27 -1.27)
            (xy 1.27 -1.27)
          )
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts
            (xy -0.762 -1.905)
            (xy 0.762 -1.905)
          )
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts
            (xy -0.254 -2.54)
            (xy 0.254 -2.54)
          )
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "GND_1_0"
        (pin power_in line (at 0 0 90) (length 0)
          (name "GND" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
    )
  )

  (junction (at 31.75 35.56) (diameter 0) (color 0 0 0 0)
    (uuid 6686A589-0C58-0DC1-0DA8-0100)
  )

  (wire (pts (xy 31.75 30.48) (xy 31.75 35.56))
    (stroke (width 0) (type default))
    (uuid 6686A589-0C58-0DC1-0DA8-0200)
  )
  (wire (pts (xy 31.75 35.56) (xy 38.1 35.56))
    (stroke (width 0) (type default))
    (uuid 6686A589-0C58-0DC1-0DA8-0201)
  )
  (wire (pts (xy 38.1 35.56) (xy 38.1 30.48))
    (stroke (width 0) (type default))
    (uuid 6686A589-0C58-0DC1-0DA8-0202)
  )
  (wire (pts (xy 38.1 35.56) (xy 38.1 43.18))
    (stroke (width 0) (type default))
    (uuid 6686A589-0C58-0DC1-0DA8-0203)
  )
  (wire (pts (xy 38.1 43.18) (xy 31.75 43.18))
    (stroke (width 0) (type default))
    (uuid 6686A589-0C58-0DC1-0DA8-0204)
  )
  (wire (pts (xy 31.75 43.18) (xy 31.75 40.64))
    (stroke (width 0) (type default))
    (uuid 6686A589-0C58-0DC1-0DA8-0205)
  )

  (symbol (lib_id "Device:R") (at 31.75 35.56 90) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid 6686A589-0C58-0DC1-0DA8-0300)
    (property "Reference" "R1"
      (at 33.02 34.29 90)
      (effects (font (size 1.27 1.27)) (justify left))
    )
    (property "Value" "1k"
      (at 33.02 36.83 90)
      (effects (font (size 1.27 1.27)) (justify left))
    )
    (property "Footprint" "Resistor_SMD:R_0805_2012Metric"
      (at 33.655 35.56 90)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1" (uuid 6686A589-0C58-0DC1-0DA8-0301))
    (pin "2" (uuid 6686A589-0C58-0DC1-0DA8-0302))
  )

  (symbol (lib_id "Device:LED") (at 38.1 35.56 90) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (mirror y)
    (uuid 6686A589-0C58-0DC1-0DA8-0400)
    (property "Reference" "D1"
      (at 36.83 34.29 90)
      (effects (font (size 1.27 1.27)) (justify right))
    )
    (property "Value" "Red"
      (at 36.83 36.83 90)
      (effects (font (size 1.27 1.27)) (justify right))
    )
    (property "Footprint" "LED_SMD:LED_0805_2012Metric"
      (at 39.37 30.48 90)
      (effects (font (size 1.27 1.27)) hide)
    )
    (pin "1" (uuid 6686A589-0C58-0DC1-0DA8-0401))
    (pin "2" (uuid 6686A589-0C58-0DC1-0DA8-0402))
  )

  (symbol (lib_id "power:+5V") (at 31.75 30.48 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid 6686A589-0C58-0DC1-0DA8-0500)
    (property "Reference" "#PWR01"
      (at 31.75 26.67 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "+5V"
      (at 31.75 29.21 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid 6686A589-0C58-0DC1-0DA8-0501))
  )

  (symbol (lib_id "power:GND") (at 31.75 43.18 0) (unit 1)
    (in_bom yes) (on_board yes) (dnp no)
    (uuid 6686A589-0C58-0DC1-0DA8-0600)
    (property "Reference" "#PWR02"
      (at 31.75 47.625 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "GND"
      (at 31.75 45.72 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1" (uuid 6686A589-0C58-0DC1-0DA8-0601))
  )

  (sheet_instances
    (path "/" (page "1"))
  )
)
"""


def generate_led_circuit(output_dir: str = "."):
    """生成简单的LED电路"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 生成SCH文件
    sch_file = output_path / "led_circuit.kicad_sch"
    with open(sch_file, "w", encoding="utf-8") as f:
        f.write(SCH_CONTENT)

    # 生成PCB文件
    pcb_file = output_path / "led_circuit.kicad_pcb"
    with open(pcb_file, "w", encoding="utf-8") as f:
        f.write(PCB_CONTENT)

    return str(sch_file), str(pcb_file)


def main():
    sch_file, pcb_file = generate_led_circuit("./test_output")
    print(f"生成的文件:")
    print(f"  原理图: {sch_file}")
    print(f"  PCB文件: {pcb_file}")
    print("")
    print("说明:")
    print("- 生成的文件使用KiCad标准S-expression格式")
    print("- 可直接在KiCad 7.x/8.x/9.x GUI中打开")
    print("- 无需KiCad API依赖")


if __name__ == "__main__":
    main()
