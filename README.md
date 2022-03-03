# umamusume skill-code converter
- 将赛马娘技能触发代码转换为描述文本





# 使用方法

- 安装Python环境

- 克隆此仓库, 并给克隆的文件夹命名(以命名为`umamusume_skill_converter`为例)
- 引用此包

```python
import umamusume_skill_converter as usc

pr = usc.UmaSkillCodeParser("cn")
print(pr.get_nature_lang("running_style==1 &is_finalcorner_random==1 &order==1"))
```

- 此时你应该可以在控制台看到输出

```
逃马, 最终弯道, 名次=1
```

