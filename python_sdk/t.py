#!/usr/bin/env python3
"""
Central Storage System - Data Generation Test Script

This script demonstrates the Python SDK capabilities by creating a complete
test environment with laboratories, storage devices, sections, and items.
"""

import sys
import time
from pathlib import Path

# Add the SDK to Python path
sdk_path = Path(__file__).parent / "central_storage_sdk"
sys.path.insert(0, str(sdk_path.parent))

from central_storage_sdk import CentralStorageClient
from central_storage_sdk.batch import BatchOperations
from central_storage_sdk.models import PaginationParams
from central_storage_sdk.exceptions import APIError, AuthenticationError


def main():
    print("🧪 Central Storage System - Test Data Generation")
    print("=" * 60)
    
    # Configuration
    BASE_URL = "http://localhost:8080"
    USERNAME = "admin"
    PASSWORD = "yht050511"  # Change this to your admin password
    
    try:
        # Initialize client
        print("🔌 Connecting to API...")
        client = CentralStorageClient(base_url=BASE_URL)
        
        # Test health check
        health = client.health_check()
        print(f"✅ API Health: {health}")
        
        # Login
        print(f"🔐 Logging in as {USERNAME}...")
        login_response = client.login(USERNAME, PASSWORD)
        print(f"✅ Login successful: {login_response.get('message', 'OK')}")
        
        # Get user profile
        profile = client.get_profile()
        print(f"👤 Logged in as: {profile.real_name or profile.username} ({profile.role})")
        
        # 电阻数据映射表 (标号 -> 阻值)
        resistor_data = {
            23: 100, 24: 30, 25: 820, 26: 27, 27: 20, 28: 1500, 29: 2700, 30: 62000,
            31: 23, 32: 3000, 33: 3900, 34: 6800, 35: 270, 36: 4700, 37: 820000, 38: 2200,
            39: 91, 40: 10, 41: 470, 42: 33000, 43: 82000, 44: 68, 45: 120000, 46: 7500,
            47: 910000, 48: 390, 49: 15000, 50: 6200, 51: 910, 52: 51, 53: 620000, 54: 75000,
            55: 39, 56: 22, 57: 15, 58: 750, 59: 510, 60: 330000, 61: 680, 62: 68000,
            63: 470, 64: 1200, 65: 120, 66: 22000, 67: 12000, 68: 220, 69: 620, 70: 51000,
            71: 680000, 72: 91000, 73: 270000, 74: 9100, 76: 20000, 77: 510000, 78: 200,
            79: 5100, 80: 300000, 81: 62
            # 75号位置为空
        }
        
        # 分区1-22的电子元件数据
        electronic_components = {
            1: {
                "name": "轻触开关",
                "description": "编带3*6*2.5MM 贴片2脚 按钮/按键 小开关2P微动轻触开关 3X6X2.5",
                "quantity": 26,
                "price": 0.09,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "3X6X2.5",
                    "component_type": "switch"
                }
            },
            2: {
                "name": "轻触开关",
                "description": "编带3*6*2.5MM 贴片2脚 按钮/按键 小开关2P微动轻触开关 3X6X2.5",
                "quantity": 32,
                "price": 0.09,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "3X6X2.5",
                    "component_type": "switch"
                }
            },
            3: {
                "name": "AMS1117-3.3V",
                "description": "AMS1117-3.3V 5.0VADJ稳压asm1117电源ic降压芯片sot-223",
                "quantity": 18,
                "price": 0.28,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "sot-223",
                    "component_type": "voltage_regulator",
                    "output_voltage": "3.3V"
                }
            },
            4: {
                "name": "LED-0603_Yellow",
                "description": "0603 LED发光二极管 黄色",
                "quantity": 22,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "LED-0603",
                    "component_type": "led",
                    "color": "yellow"
                }
            },
            5: {
                "name": "LED-0603_White",
                "description": "0603 LED发光二极管 白色",
                "quantity": 28,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "LED-0603",
                    "component_type": "led",
                    "color": "white"
                }
            },
            6: {
                "name": "LED-0603_Red",
                "description": "0603 LED发光二极管 红色",
                "quantity": 26,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "LED-0603",
                    "component_type": "led",
                    "color": "red"
                }
            },
            7: {
                "name": "LED-0603_Blue",
                "description": "0603 LED发光二极管 蓝色",
                "quantity": 16,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "LED-0603",
                    "component_type": "led",
                    "color": "blue"
                }
            },
            8: {
                "name": "LED-0603_Green",
                "description": "0603 LED发光二极管 绿色",
                "quantity": 28,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "LED-0603",
                    "component_type": "led",
                    "color": "green"
                }
            },
            9: {
                "name": "TP4333",
                "description": "TP4333 SOP8 4.2V 1A 升压IC 移动电源 天源",
                "quantity": 5,
                "price": 0.56,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "SOP8",
                    "component_type": "boost_converter",
                    "output_voltage": "4.2V",
                    "output_current": "1A"
                }
            },
            10: {
                "name": "10NF 0603贴片电容",
                "description": "0603 贴片电容 10NF(103)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "10nF",
                    "code": "103"
                }
            },
            11: {
                "name": "33PF 0603贴片电容",
                "description": "0603 贴片电容 33PF(330)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "33pF",
                    "code": "330"
                }
            },
            12: {
                "name": "180PF 0603贴片电容",
                "description": "0603 贴片电容 180PF(181)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "180pF",
                    "code": "181"
                }
            },
            13: {
                "name": "68NF 0603贴片电容",
                "description": "0603 贴片电容 68NF(683)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "68nF",
                    "code": "683"
                }
            },
            14: {
                "name": "47NF 0603贴片电容",
                "description": "0603 贴片电容 47NF(473)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "47nF",
                    "code": "473"
                }
            },
            15: {
                "name": "20PF 0603贴片电容",
                "description": "0603 贴片电容 20PF(200)",
                "quantity": 19,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "20pF",
                    "code": "200"
                }
            },
            16: {
                "name": "4.7UF 0603贴片电容",
                "description": "0603 贴片电容 4.7UF(475)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "4.7µF",
                    "code": "475"
                }
            },
            17: {
                "name": "1NF 0603贴片电容",
                "description": "0603 贴片电容 1NF(102)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "1nF",
                    "code": "102"
                }
            },
            18: {
                "name": "30PF 0603贴片电容",
                "description": "0603 贴片电容 30PF(300)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "30pF",
                    "code": "300"
                }
            },
            19: {
                "name": "6.8PF 0603贴片电容",
                "description": "0603 贴片电容 6.8PF(6P8)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "6.8pF",
                    "code": "6P8"
                }
            },
            20: {
                "name": "150PF 0603贴片电容",
                "description": "0603 贴片电容 150PF(151)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "150pF",
                    "code": "151"
                }
            },
            21: {
                "name": "330PF 0603贴片电容",
                "description": "0603 贴片电容 330PF(331)",
                "quantity": 20,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "330pF",
                    "code": "331"
                }
            },
            22: {
                "name": "1UF 0603贴片电容",
                "description": "0603 贴片电容 1UF(105)",
                "quantity": 17,
                "price": 0.01,
                "properties": {
                    "electron_component_type": "SMD",
                    "package": "C0603",
                    "component_type": "capacitor",
                    "capacitance": "1µF",
                    "code": "105"
                }
            }
        }
        
        def format_resistance_value(ohms):
            """将电阻值格式化为标准表示法"""
            if ohms >= 1000000:
                return f"{ohms / 1000000:.1f}MΩ".rstrip('0').rstrip('.')
            elif ohms >= 1000:
                return f"{ohms / 1000:.1f}kΩ".rstrip('0').rstrip('.')
            else:
                return f"{ohms}Ω"
        
        def get_resistor_code(ohms):
            """生成电阻器编码"""
            return f"R{ohms:07d}"
        
        def get_color_code(ohms):
            """获取电阻色环编码 (简化版)"""
            # 这是一个简化的色环编码，实际应用中可能需要更复杂的算法
            colors = ["黑", "棕", "红", "橙", "黄", "绿", "蓝", "紫", "灰", "白"]
            if ohms < 10:
                return f"{colors[ohms]}黑金"
            elif ohms < 100:
                tens = ohms // 10
                ones = ohms % 10
                return f"{colors[tens]}{colors[ones]}金"
            else:
                # 简化处理，实际色环编码更复杂
                return "标准色环"
        
        print("\n📦 开始添加电子元件到对应分区...")
        
        # 获取存储设备ID为2的所有分区
        try:
            sections_response = client.get_sections_by_storage(storage_id=2)
            sections = sections_response.data
            
            # 清空现有物品
            for j in sections:
                print(f"分区: {j.name} (ID: {j.id}, 状态: {j.status})")
                d = client.get_items(section_id=j.id).data
                for i in d:
                    client.delete_item(i.id)
                    print(f"已删除物品: {i.name} (ID: {i.id})")
            time.sleep(1)
            
            # 创建分区ID映射 (SEC编号 -> 分区ID)
            section_map = {}
            for section in sections:
                if section.code.startswith("SEC"):
                    try:
                        sec_num = int(section.code[3:])  # 提取SEC后的数字
                        section_map[sec_num] = section.id
                    except ValueError:
                        continue
            
            print(f"找到 {len(section_map)} 个匹配的分区")
            
            # 添加分区1-22的电子元件
            created_components = 0
            for sec_num, component_data in electronic_components.items():
                if sec_num not in section_map:
                    print(f"⚠️  警告: 找不到分区 SEC{sec_num:02d}")
                    continue
                
                section_id = section_map[sec_num]
                
                # 生成元件编码
                component_code = f"EC{sec_num:02d}{component_data['name'][:3]}"
                
                # 创建电子元件物品
                item_data = {
                    "code": component_code,
                    "name": component_data["name"],
                    "description": component_data["description"],
                    "category": "电子元件",
                    "quantity": component_data["quantity"],
                    "min_quantity": max(1, component_data["quantity"] // 4),  # 最小库存为数量的1/4
                    "unit": "个",
                    "price": component_data["price"],
                    "supplier": "电子元件供应商",
                    "section_id": section_id,
                    "properties": component_data["properties"]
                }
                
                try:
                    item = client.create_item(item_data)
                    created_components += 1
                    print(f"✅ 创建电子元件: SEC{sec_num:02d} -> {component_data['name']} (ID: {item.id}) - 数量: {component_data['quantity']}")
                except Exception as e:
                    print(f"❌ 创建失败 SEC{sec_num:02d}: {e}")
            
            print(f"\n🎉 电子元件添加完成! 成功创建 {created_components} 个电子元件")
            
            # 为每个电阻数据创建物品
            created_count = 0
            for sec_num, resistance_ohms in resistor_data.items():
                if sec_num not in section_map:
                    print(f"⚠️  警告: 找不到分区 SEC{sec_num:02d}")
                    continue
                
                section_id = section_map[sec_num]
                resistance_text = format_resistance_value(resistance_ohms)
                resistor_code = get_resistor_code(resistance_ohms)
                color_code = get_color_code(resistance_ohms)
                
                # 创建电阻器物品
                item_data = {
                    "code": resistor_code,
                    "name": f"0603贴片电阻 {resistance_text}",
                    "description": f"标准贴片电阻器，封装：0603，阻值 {resistance_text}，色环编码: {color_code}",
                    "category": "电子元件",
                    "quantity": 50,  # 默认数量
                    "min_quantity": 10,  # 最小库存
                    "unit": "个",
                    "price": 0.01,  # 默认单价
                    "supplier": "未知",
                    "section_id": section_id,
                    "properties": {
                        "component_type": "resistor",
                        "resistance_ohms": resistance_ohms,
                        "resistance_text": resistance_text,
                        "tolerance": "±5%",
                        "power_rating": "1/4W",
                        "package": "R0603",
                        "color_code": color_code,
                        "temperature_coefficient": "±100ppm/°C",
                        "material": "厚膜"
                    }
                }
                
                try:
                    item = client.create_item(item_data)
                    created_count += 1
                    print(f"✅ 创建电阻: SEC{sec_num:02d} -> {resistance_text} (ID: {item.id})")
                except Exception as e:
                    print(f"❌ 创建失败 SEC{sec_num:02d}: {e}")
            
            # 处理75号空位置
            if 75 in section_map:
                print(f"ℹ️  分区 SEC75 保持为空 (按要求)")
            
            print(f"\n🎉 总计添加完成! 电子元件: {created_components} 个，电阻器: {created_count} 个")
            
        except Exception as e:
            print(f"❌ 获取分区信息失败: {e}")
        

    except AuthenticationError:
        print("❌ Authentication failed. Please check your credentials.")
    except APIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
