# KiCad 嘉立创打样模板 / JLC Prototype Templates

用于 KiCad 10 的两层、四层 FR4 / 1 oz 空白工程模板。保留经过实际 PCB 调整的常用设计规则，并清除器件、走线、网络、板框、项目专用库和历史 DRC 排除。

| 模板 | 默认过孔（外径／孔径） | 最小过孔外径／孔径 | 最小线宽／线距 |
|---|---|---|---|
| `jlc-2layer-1oz-prototype` | 0.50／0.30 mm | 0.50／0.30 mm | 0.127／0.127 mm |
| `jlc-4layer-1oz-prototype` | 0.45／0.20 mm | 0.40／0.20 mm | 0.127／0.127 mm |

共同设置：1.6 mm 标称板厚，默认走线宽 0.20 mm，丝印距焊盘 0.15 mm，默认丝印字高 1 mm、笔画 0.15 mm，过孔默认双面盖油。四层模板的 0.127 mm 线宽规则同时适用于内层和外层。

模板不依赖 0.15 mm 非常规钻孔。具体板价、优惠、工厂接单能力仍以订单审核为准。

## 使用

1. 在 KiCad 的“首选项 → 配置路径”查看 `KICAD_USER_TEMPLATE_DIR`。
2. 将 `templates/` 中的两个模板文件夹复制到该目录，保留各自的 `meta/info.html`。
3. 打开“文件 → 新建工程”，选择 **JLC 2L / 1oz Prototype** 或 **JLC 4L / 1oz Prototype**。较旧界面可能叫“从模板新建工程”。
4. 新工程会自动按你输入的名称重命名工程、原理图、PCB 和 `.kicad_dru` 文件。
5. 先画闭合板框，再开始放置器件。空白模板故意没有板框；画板框前 DRC 提示无有效板框属于预期。

Windows 可运行：

```powershell
.\tools\install.ps1
# 如果 KiCad 配置了其他个人模板目录：
.\tools\install.ps1 -Destination '你的 KICAD_USER_TEMPLATE_DIR'
```

脚本默认安装到系统“文档”目录下的 `KiCad/10.0/template`，支持“文档”重定向；不会覆盖内容不同的同名模板。

## 规则边界

详见 [RULES.md](RULES.md)。0.127 mm 是本模板选用的设计余量，不是嘉立创四层板的制造极限；0.20 mm 的焊盘到走线间距、0.15 mm 的文字笔画也包含设计选择。模板不提供统一的电压绝缘认证或载流能力保证。

KiCad 公共库的部分小器件外框距焊盘约 0.10 mm，仍可能触发本模板 0.15 mm 的丝印检查。需要在 PCB 内调整/裁剪外框或使用自己的封装库，模板不会修改电脑上的公共库。

## 验证

```sh
python tools/validate.py --kicad-cli /path/to/kicad-cli --report validation/summary.json
python tools/validate.py --structure-only
```

完整检查会模拟工程重命名、加载原理图、添加临时板框，并用真实 DRC 验证小线宽、小过孔、小孔环、小间距和丝印违规能被检出。测试对象只存在于临时目录。仓库内的 `validation/summary.json` 保存最近一次完整验证结果；CI 只运行文件结构检查，不冒充完整 DRC。

## English

Two blank KiCad 10 project templates for 2-layer and 4-layer FR4 / 1 oz prototypes. Copy the folders under `templates/` into `KICAD_USER_TEMPLATE_DIR`, then create a new project using the KiCad template selector. Project files and the custom-rule file are renamed together.

The selected track minimum is 0.127 mm on all copper layers. Default vias are 0.50/0.30 mm for two layers and 0.45/0.20 mm for four layers (outer/drill). No board outline, components, local libraries, project nets, or historical DRC exclusions are included. Draw an outline before running a normal board DRC. Read `RULES.md` before using these manufacturing baselines.

## 来源与许可

- [KiCad 10 工程模板文档](https://docs.kicad.org/10.0/en/kicad/kicad.html#project-templates)
- [嘉立创制造工艺要求](https://www.jlc.com/portal/1/serviceGuide)
- [嘉立创工艺能力总表](https://www.jlc.com/portal/vtechnology.html)

参数核对日期：2026-11-08。采用 MIT 许可；不代表嘉立创或 KiCad 官方模板。
