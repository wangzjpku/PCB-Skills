# KiCad 源码调试指南

## 源码位置
本目录包含完整的KiCad源代码，用于开发和调试PCB-Skill项目。

- **目录**: `kicad-source/`
- **来源**: https://gitlab.com/kicad/code/kicad.git
- **大小**: ~944MB
- **版本**: 最新开发版 (shallow clone)

## 关键目录说明

### 1. 文件格式解析代码
```
kicad-source/
├── common/io/              # IO通用代码
├── eeschema/sch_io/        # 原理图文件读写
│   └── kicad_sexpr/        # S-expression格式解析
└── pcbnew/pcb_io/          # PCB文件读写
    └── kicad_sexpr/        # PCB S-expression格式
```

### 2. 核心编辑器源码
```
kicad-source/
├── eeschema/               # 原理图编辑器 (Eeschema)
│   ├── sch_*.cpp/h         # 原理图各类元素
│   ├── lib_symbol.cpp      # 符号库
│   └── symbol_editor/      # 符号编辑器
├── pcbnew/                 # PCB编辑器 (Pcbnew)
│   ├── board*.cpp          # PCB板实现
│   ├── track.cpp           # 走线
│   ├── footprint.cpp       # 封装
│   └── autorouter/         # 自动布线
└── include/                # 头文件
```

## 如何使用源码调试Skill

### 1. 对比文件格式
当skill生成的文件有错误时，可以对比KiCad源码中的格式定义：

```bash
# 查看原理图符号的S-expression格式定义
grep -r "symbol" kicad-source/eeschema/sch_io/kicad_sexpr/*.cpp | head -20

# 查看PCB封装的格式定义  
grep -r "footprint" kicad-source/pcbnew/pcb_io/kicad_sexpr/*.cpp | head -20
```

### 2. 查看默认参数
```bash
# 查看原理图默认值
cat kicad-source/eeschema/default_values.h

# 查看PCB设计规则默认值
cat kicad-source/pcbnew/board_design_settings.cpp
```

### 3. 学习解析逻辑
```bash
# 查看错误处理
grep -r "throw" kicad-source/eeschema/sch_io/kicad_sexpr/*.cpp | head -10
grep -r "throw" kicad-source/pcbnew/pcb_io/kicad_sexpr/*.cpp | head -10
```

## 调试示例

### 原理图格式调试
```bash
# 查看原理图符号定义
cat kicad-source/eeschema/lib_symbol.h

# 查看原理图文件解析
cat kicad-source/eeschema/sch_io/kicad_sexpr/sch_io_kicad_sexpr.cpp
```

### PCB格式调试
```bash
# 查看PCB封装定义
cat kicad-source/pcbnew/footprint.h

# 查看PCB文件解析
cat kicad-source/pcbnew/pcb_io/kicad_sexpr/pcb_io_kicad_sexpr.cpp
```

## 更新KiCad源码

```bash
cd kicad-source
git pull origin main
cd ..
```

## 参考链接

- KiCad 官方: https://www.kicad.org/
- KiCad GitLab: https://gitlab.com/kicad/code/kicad
- 文件格式文档: https://dev-docs.kicad.org/en/file-formats/
