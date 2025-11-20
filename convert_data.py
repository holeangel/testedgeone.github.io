import json

# 读取爬取的数据
with open('medicines.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 转换为JavaScript格式
js_data = {}
for item in data:
    if item['dosage']:
        # 解析用量范围
        dosage_str = item['dosage']
        # 提取最小和最大值
        import re
        # 匹配格式：3～6g, 0.15～0.35g 等
        match = re.search(r'(\d+(?:\.\d+)?)[～~\-](\d+(?:\.\d+)?)g', dosage_str)
        if match:
            min_val = float(match.group(1))
            max_val = float(match.group(2))
            js_data[item['title']] = {
                'min': min_val,
                'max': max_val,
                'text': item['dosage_text']
            }
        else:
            # 单个值的情况
            match_single = re.search(r'(\d+(?:\.\d+)?)g', dosage_str)
            if match_single:
                val = float(match_single.group(1))
                js_data[item['title']] = {
                    'min': val,
                    'max': val,
                    'text': item['dosage_text']
                }

# 输出JavaScript格式到文件
with open('medicine_data.js', 'w', encoding='utf-8') as f:
    f.write(f"// 共 {len(js_data)} 种药物的用量数据\n")
    f.write("const medicineDosageData = " + json.dumps(js_data, ensure_ascii=False, indent=2) + ";\n")
    f.write(f"\n// 统计：共 {len(js_data)} 种药物有用量数据\n")

print(f"已生成 medicine_data.js，包含 {len(js_data)} 种药物的用量数据")
