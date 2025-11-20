import requests
import re
from bs4 import BeautifulSoup
import json
import time

class MedicineCrawler:
    def __init__(self):
        self.base_url = "https://ydz.chp.org.cn/front-api/entry/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_medicine_info(self, entry_id):
        """获取单个药品信息"""
        try:
            url = f"{self.base_url}{entry_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['code'] == 200 and data['data']:
                    return self.parse_medicine_data(data['data'])
            
            return None
        
        except Exception as e:
            print(f"请求失败 ID={entry_id}: {e}")
            return None
    
    def parse_medicine_data(self, data):
        """解析药品数据"""
        result = {
            'entry_id': data.get('entryId'),
            'title': data.get('title'),
            'pinyin': data.get('pinyinTitle'),
            'dosage': None,
            'dosage_text': None
        }
        
        # 解析HTML内容，提取用法用量
        html_content = data.get('htmlContent', '')
        if html_content:
            dosage_info = self.extract_dosage(html_content)
            result['dosage'] = dosage_info['dosage']
            result['dosage_text'] = dosage_info['text']
        
        return result
    
    def extract_dosage(self, html_content):
        """从HTML中提取用法用量"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找【用法与用量】部分
        for tag in soup.find_all(['p', 'b']):
            if '【用法与用量】' in tag.get_text():
                # 获取下一个<p>标签的内容
                next_p = tag.find_next('p')
                if next_p:
                    text = next_p.get_text()
                    # 使用正则提取克数，支持多种格式
                    # 匹配: 3～6g, 3-6g, 3~6g, 3g, 0.3～0.6g 等
                    dosage_pattern = r'(\d+(?:\.\d+)?[～~\-]\d+(?:\.\d+)?g|\d+(?:\.\d+)?g)'
                    match = re.search(dosage_pattern, text)
                    
                    if match:
                        return {
                            'dosage': match.group(1),
                            'text': text.strip()
                        }
        
        return {'dosage': None, 'text': None}
    
    def crawl_range(self, start_id, end_id):
        """批量爬取指定范围的药品"""
        results = []
        
        for entry_id in range(start_id, end_id + 1):
            print(f"正在爬取 ID: {entry_id}")
            
            info = self.get_medicine_info(entry_id)
            
            if info:
                results.append(info)
                print(f"  ✓ {info['title']} - 用量: {info['dosage']}，用法: {info['dosage_text']}")
            else:
                print(f"  ✗ 未找到数据")
            
            # 避免请求过快，添加延迟
            time.sleep(0.5)
        
        return results
    
    def save_to_file(self, results, filename='medicines.json'):
        """保存结果到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n数据已保存到 {filename}")


# 使用示例
if __name__ == "__main__":
    crawler = MedicineCrawler()
    
    # 示例1: 获取单个药品信息
    print("=== 示例1: 获取单个药品 ===")
    info = crawler.get_medicine_info(2)
    if info:
        print(f"药品名称: {info['title']}")
        print(f"拼音: {info['pinyin']}")
        print(f"用量: {info['dosage']}")
        print(f"完整用法: {info['dosage_text']}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 批量爬取（爬取ID 2-615，获取全部药物数据）
    print("=== 示例2: 批量爬取 ===")
    results = crawler.crawl_range(2, 615)
    
    # 保存结果
    crawler.save_to_file(results)
    
    # 打印统计
    print(f"\n总共爬取: {len(results)} 条数据")
    print(f"有用量信息: {sum(1 for r in results if r['dosage'])} 条")
