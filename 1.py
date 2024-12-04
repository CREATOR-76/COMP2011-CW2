import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import random
from app import app, db
from app.models import Product, Category, User, Order, Cart, OrderItem

def import_products_from_csv(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path)
    # 首先确保基础类别存在
    categories = {
        'Men': ensure_category('Men', 'Men Shoes'),
        'Women': ensure_category('Women', 'Women Shoes'),
        'Boys': ensure_category('Boys', 'Boys Clothes'),
        'Girls': ensure_category('Girls', 'Girls Clothes')
    }
    # 导入商品数据
    for _, row in df.iterrows():
        # 获取对应的类别ID
        category = categories.get(row['Gender'])
        if not category:
            print(f"跳过商品 {row['ProductTitle']}: 未知类别 {row['Gender']}")
            continue
        # 创建更丰富的商品描述
        description = f"This {row['ProductTitle'].lower()} is a {row['ProductType'].lower()} "
        description += f"designed for {row['Gender'].lower()}. "
        description += f"It comes in a stylish {row['Colour'].lower()} color "
        description += f"and is perfect for {row['Usage'].lower()}. "
        # 随机生成价格（英镑）
        sample_price = round(random.uniform(8, 80), 2)  # 调整为更合理的英镑价格范围
        product = Product(
            name=row['ProductTitle'],
            price=sample_price,
            description=description,
            stock=random.randint(10, 100),
            image_url=row['ImageURL'],
            Gender=row['Gender'],
            color=row['Colour'],
            product_type=row['ProductType'],
            usage=row['Usage'],
            category_id=category.id,
            click_count=0  # 设置初始点击次数为0
        )
        db.session.add(product)
    try:
        db.session.commit()
        print("Data import successful!")
    except Exception as e:
        db.session.rollback()
        print(f"Import error: {str(e)}")

def ensure_category(name, description):
    """确保类别存在，如果不存在则创建"""
    category = Category.query.filter_by(name=name).first()
    if not category:
        category = Category(
            name=name,
            description=description,
            click_count=0  # 设置类别初始点击次数为0
        )
        db.session.add(category)
        db.session.commit()
    return category

if __name__ == "__main__":
    with app.app_context():
        import_products_from_csv('fashion.csv')