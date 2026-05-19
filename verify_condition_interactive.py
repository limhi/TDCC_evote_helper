#!/usr/bin/env python3
# coding: utf-8
"""
TDCC 投票流程 - 交互式 Condition 验证工具

功能：
  - 启动浏览器，不自动操作
  - 手动操作网页，同时在 Python 中测试 condition
  - 支持实时调整选择器和超时时间
  - 保存验证成功的条件配置
  - 显示详细的调试信息

使用方法：
  1. python verify_condition_interactive.py
  2. 按照菜单指引，手动操作网页
  3. 在各个步骤测试对应的 condition
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================================================================
# 预定义的条件配置（根据 TDCC 投票流程）
# ============================================================================

PREDEFINED_CONDITIONS = {
    "1_login_page": {
        "name": "1. 登入页面 - 身分证输入框",
        "locator": (By.NAME, "pageIdNo"),
        "condition_type": "presence",
        "description": "检查身份证输入框是否存在"
    },
    
    "2_login_confirmation": {
        "name": "2. 登入确认 - 确认对话框按钮",
        "locator": (By.ID, "comfirmDialog_okBtn"),
        "condition_type": "presence",
        "description": "检查登入确认对话框是否出现",
        "optional": True
    },
    
    "3_terms_agreement": {
        "name": "3. 条款同意 - 同意按钮",
        "locator": (By.CSS_SELECTOR, 'a[class="btnAgree btn-style btn-b btn-lg"]'),
        "condition_type": "clickable",
        "description": "检查条款同意按钮是否可点击",
        "optional": True
    },
    
    "4_stock_list_page": {
        "name": "4. 股票清单页面 - 股票ID输入框",
        "locator": (By.NAME, 'qryStockId'),
        "condition_type": "presence",
        "description": "检查股票ID搜索框是否加载"
    },
    
    "5_voting_page_table": {
        "name": "5. 投票页面 - 投票表格",
        "locator": (By.TAG_NAME, 'table'),
        "condition_type": "visibility",
        "description": "检查投票表格是否可见"
    },
    
    "6_accept_button": {
        "name": "6. 投票选项 - 全部赞成按钮",
        "locator": (By.CSS_SELECTOR, 'table.c-votelist_docSection tr:nth-child(2) td:nth-child(2) a:nth-child(1)'),
        "condition_type": "clickable",
        "description": "检查'全部赞成'按钮是否可点击"
    },
    
    "7_vote_complete": {
        "name": "7. 投票完成 - '投票已完成'文本",
        "locator": (By.TAG_NAME, 'table'),
        "condition_type": "text",
        "text": "投票已完成",
        "description": "检查表格中是否出现'投票已完成'文本"
    },
    
    "8_process_button": {
        "name": "8. 投票完成 - 完成按钮",
        "locator": (By.CSS_SELECTOR, 'button[onclick="doProcess();"]'),
        "condition_type": "clickable",
        "description": "检查完成按钮是否可点击"
    },
    
    "9_msg_dialog": {
        "name": "9. 消息对话框 - 确认按钮",
        "locator": (By.ID, "msgDialog_okBtn"),
        "condition_type": "presence",
        "description": "检查消息对话框确认按钮",
        "optional": True
    },
}

# ============================================================================
# 核心验证函数
# ============================================================================

def test_single_condition(driver, locator, condition_type, text=None, timeout=10):
    """
    测试单个 condition
    
    参数：
        driver: WebDriver 对象
        locator: (By.xxx, "selector")
        condition_type: "presence" | "visibility" | "clickable" | "text"
        text: 当 condition_type="text" 时，检查的文本内容
        timeout: 等待超时秒数
    
    返回：
        (success: bool, message: str, element: WebElement or None)
    """
    try:
        start_time = time.time()
        
        if condition_type == "presence":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            elapsed = time.time() - start_time
            return True, f"✅ 元素存在 (耗时 {elapsed:.2f}秒)", element
        
        elif condition_type == "visibility":
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            elapsed = time.time() - start_time
            return True, f"✅ 元素可见 (耗时 {elapsed:.2f}秒)", element
        
        elif condition_type == "clickable":
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            elapsed = time.time() - start_time
            return True, f"✅ 元素可点击 (耗时 {elapsed:.2f}秒)", element
        
        elif condition_type == "text":
            element = WebDriverWait(driver, timeout).until(
                EC.text_to_be_present_in_element(locator, text)
            )
            elapsed = time.time() - start_time
            return True, f"✅ 文本'{text}'存在 (耗时 {elapsed:.2f}秒)", element
        
        else:
            return False, f"❌ 未知的 condition_type: {condition_type}", None
    
    except TimeoutException:
        return False, f"❌ 超时：在 {timeout} 秒内未找到条件", None
    except NoSuchElementException as e:
        return False, f"❌ 元素不存在：{e}", None
    except Exception as e:
        return False, f"❌ 异常：{str(e)}", None


def get_element_info(driver, locator):
    """获取元素的详细信息（用于调试）"""
    try:
        element = driver.find_element(*locator)
        info = {
            "tag": element.tag_name,
            "class": element.get_attribute("class"),
            "id": element.get_attribute("id"),
            "text": element.text[:50] if element.text else "(无文本)",
            "visible": element.is_displayed(),
            "enabled": element.is_enabled(),
            "outer_html": element.get_attribute("outerHTML")[:100]
        }
        return info
    except Exception as e:
        return {"error": str(e)}


def print_header(title):
    """打印美化的标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_menu():
    """打印主菜单"""
    print_header("TDCC 投票流程 - 交互式 Condition 验证工具")
    print("\n预定义的 Condition 列表：\n")
    
    for idx, (key, config) in enumerate(PREDEFINED_CONDITIONS.items(), 1):
        optional = " [可选]" if config.get("optional") else ""
        print(f"  {idx}. {config['name']}{optional}")
        print(f"     └─ {config['description']}\n")
    
    print(f"  {len(PREDEFINED_CONDITIONS) + 1}. 自定义 Condition 测试")
    print(f"  {len(PREDEFINED_CONDITIONS) + 2}. 查看页面结构信息")
    print(f"  {len(PREDEFINED_CONDITIONS) + 3}. 保存当前验证结果")
    print(f"  {len(PREDEFINED_CONDITIONS) + 4}. 退出\n")


def print_condition_config(config):
    """打印 condition 的配置信息"""
    print(f"\n【条件配置】")
    print(f"  名称：{config['name']}")
    print(f"  定位器：{config['locator']}")
    print(f"  条件类型：{config['condition_type']}")
    if 'text' in config:
        print(f"  文本内容：{config['text']}")
    print(f"  说明：{config['description']}")


def test_predefined_condition(driver, condition_key):
    """测试预定义的 condition"""
    if condition_key not in PREDEFINED_CONDITIONS:
        print(f"❌ 条件不存在：{condition_key}")
        return
    
    config = PREDEFINED_CONDITIONS[condition_key]
    print_condition_config(config)
    
    # 获取超时时间
    while True:
        try:
            timeout_input = input(f"\n请输入超时时间（默认 10 秒，直接按 Enter）: ").strip()
            timeout = int(timeout_input) if timeout_input else 10
            if timeout > 0:
                break
            print("❌ 请输入正整数")
        except ValueError:
            print("❌ 输入无效，请输入数字")
    
    # 执行测试
    print(f"\n⏳ 开始测试（超时：{timeout}秒）...")
    print("（请在浏览器中进行相应操作...）\n")
    
    locator = config['locator']
    condition_type = config['condition_type']
    text = config.get('text')
    
    success, message, element = test_single_condition(
        driver, locator, condition_type, text, timeout
    )
    
    print(message)
    
    if success and element:
        print("\n【元素信息】")
        info = get_element_info(driver, locator)
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    return success, config


def test_custom_condition(driver):
    """测试自定义 condition"""
    print_header("自定义 Condition 测试")
    
    print("\n支持的定位方式:")
    locator_types = {
        "1": (By.ID, "ID"),
        "2": (By.NAME, "NAME"),
        "3": (By.CLASS_NAME, "CLASS_NAME"),
        "4": (By.TAG_NAME, "TAG_NAME"),
        "5": (By.CSS_SELECTOR, "CSS_SELECTOR"),
        "6": (By.XPATH, "XPATH"),
    }
    
    for key, (by_type, name) in locator_types.items():
        print(f"  {key}. {name}")
    
    while True:
        choice = input("\n请选择定位方式（1-6）: ").strip()
        if choice in locator_types:
            by_type, type_name = locator_types[choice]
            break
        print("❌ 输入无效，请选择 1-6")
    
    selector = input(f"请输入 {type_name} 值: ").strip()
    
    print("\n支持的 Condition 类型:")
    condition_types = {
        "1": "presence",
        "2": "visibility",
        "3": "clickable",
        "4": "text",
    }
    
    for key, ctype in condition_types.items():
        print(f"  {key}. {ctype}")
    
    while True:
        choice = input("\n请选择 Condition 类型（1-4）: ").strip()
        if choice in condition_types:
            condition_type = condition_types[choice]
            break
        print("❌ 输入无效，请选择 1-4")
    
    text = None
    if condition_type == "text":
        text = input("请输入要匹配的文本: ").strip()
    
    timeout = 10
    while True:
        try:
            timeout_input = input(f"请输入超时时间（默认 10 秒）: ").strip()
            timeout = int(timeout_input) if timeout_input else 10
            if timeout > 0:
                break
            print("❌ 请输入正整数")
        except ValueError:
            print("❌ 输入无效，请输入数字")
    
    # 执行测试
    print(f"\n⏳ 开始测试（超时：{timeout}秒）...")
    print("（请在浏览器中进行相应操作...）\n")
    
    locator = (by_type, selector)
    success, message, element = test_single_condition(
        driver, locator, condition_type, text, timeout
    )
    
    print(message)
    
    if success and element:
        print("\n【元素信息】")
        info = get_element_info(driver, locator)
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    return success, {
        "name": f"自定义条件",
        "locator": locator,
        "condition_type": condition_type,
        "text": text,
        "selector_str": f"{type_name}={selector}"
    }


def show_page_structure(driver):
    """显示页面的结构信息"""
    print_header("页面结构信息")
    
    print("\n【页面 URL】")
    print(f"  {driver.current_url}")
    
    print("\n【页面标题】")
    print(f"  {driver.title}")
    
    print("\n【主要表单元素】")
    try:
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"  输入框数量：{len(inputs)}")
        for i, inp in enumerate(inputs[:10]):
            name = inp.get_attribute("name")
            type_ = inp.get_attribute("type")
            print(f"    {i+1}. name='{name}' type='{type_}'")
    except Exception as e:
        print(f"  ❌ 错误：{e}")
    
    print("\n【主要按钮元素】")
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"  按钮数量：{len(buttons)}")
        for i, btn in enumerate(buttons[:10]):
            onclick = btn.get_attribute("onclick")
            text = btn.text[:30]
            print(f"    {i+1}. onclick='{onclick}' text='{text}'")
    except Exception as e:
        print(f"  ❌ 错误：{e}")
    
    print("\n【主要表格信息】")
    try:
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"  表格数量：{len(tables)}")
        for i, table in enumerate(tables[:5]):
            class_attr = table.get_attribute("class")
            rows = len(table.find_elements(By.TAG_NAME, "tr"))
            print(f"    {i+1}. class='{class_attr}' rows={rows}")
            print(f"       内容（前100字）: {table.text[:100]}")
    except Exception as e:
        print(f"  ❌ 错误：{e}")
    
    print("\n【单选按钮行（投票用）】")
    try:
        rows = driver.find_elements(By.XPATH, '//td/input[@type="radio"]/../..')
        print(f"  投票行数量：{len(rows)}")
    except Exception as e:
        print(f"  ❌ 错误：{e}")


def save_results(verified_conditions):
    """保存验证成功的条件到文件"""
    if not verified_conditions:
        print("❌ 没有验证成功的条件")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"verified_conditions_{timestamp}.json"
    
    output = {
        "timestamp": timestamp,
        "conditions": []
    }
    
    for success, config in verified_conditions:
        if success:
            if isinstance(config['locator'], tuple):
                by_type, selector = config['locator']
                locator_str = f"{by_type}={selector}"
            else:
                locator_str = str(config['locator'])
            
            output['conditions'].append({
                "name": config.get('name', '未命名'),
                "locator": locator_str,
                "condition_type": config.get('condition_type'),
                "text": config.get('text'),
                "description": config.get('description', '')
            })
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"✅ 验证结果已保存到：{filename}")
        print(f"   共保存 {len(output['conditions'])} 个条件")
    except Exception as e:
        print(f"❌ 保存失败：{e}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主程序入口"""
    print_header("TDCC 投票流程 - 交互式 Condition 验证工具")
    
    print("\n💡 使用说明：")
    print("  1. 程序启动后，浏览器会打开 TDCC 登入页面")
    print("  2. 你可以手动操作浏览器进行投票流程")
    print("  3. 在命令行中选择对应的步骤来验证 Condition")
    print("  4. 观察每个 Condition 是否能正确检测到页面元素")
    print("  5. 验证完成后，可以保存成功的条件配置\n")
    
    input("按 Enter 启动浏览器...")
    
    # 启动浏览器
    print("\n⏳ 启动 Chrome 浏览器...")
    driver = webdriver.Chrome()  # 确保 chromedriver 在 PATH 中
    
    driver.get("https://stockservices.tdcc.com.tw/evote/login/shareholder.html")
    print("✅ 浏览器已启动")
    print("⏳ 请完成登入和投票步骤，然后在命令行中选择要测试的 Condition\n")
    
    verified_conditions = []
    
    try:
        while True:
            print_menu()
            choice = input("请选择（输入数字）: ").strip()
            
            if not choice:
                print("❌ 请输入有效选择")
                continue
            
            # 预定义条件
            if choice.isdigit() and 1 <= int(choice) <= len(PREDEFINED_CONDITIONS):
                condition_key = list(PREDEFINED_CONDITIONS.keys())[int(choice) - 1]
                success, config = test_predefined_condition(driver, condition_key)
                verified_conditions.append((success, config))
            
            # 自定义条件
            elif choice == str(len(PREDEFINED_CONDITIONS) + 1):
                success, config = test_custom_condition(driver)
                verified_conditions.append((success, config))
            
            # 查看页面结构
            elif choice == str(len(PREDEFINED_CONDITIONS) + 2):
                show_page_structure(driver)
            
            # 保存结果
            elif choice == str(len(PREDEFINED_CONDITIONS) + 3):
                save_results(verified_conditions)
            
            # 退出
            elif choice == str(len(PREDEFINED_CONDITIONS) + 4):
                print("\n👋 感谢使用，正在关闭浏览器...")
                break
            
            else:
                print("❌ 选择无效，请输入正确的数字")
            
            input("\n按 Enter 继续...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断程序")
    finally:
        driver.quit()
        print("✅ 浏览器已关闭")


if __name__ == "__main__":
    main()
