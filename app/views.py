from flask import render_template, redirect, url_for, flash, jsonify
from app import app, db
from app.forms import SearchForm
from app.models import Product, Category
from flask import request
from datetime import datetime, date, time
from random import sample

# 创建上下文处理器
@app.context_processor
def base_context():
    search_form = SearchForm()
    return dict(search_form=search_form)

@app.route('/')
def index():
    categories = Category.query.all()

    hot_categories = Category.query.order_by(Category.click_count.desc()).limit(3).all()

    category_products = {}
    for category in hot_categories:
        # 获取该分类下的所有商品
        all_products = Product.query.filter_by(category_id=category.id).all()
        # 如果商品数量大于4，随机选择4个；否则使用所有商品
        if len(all_products) > 4:
            products = sample(all_products, 4)
        else:
            products = all_products
        category_products[category] = products

    return render_template('index.html',
                           categories=categories,
                           hot_categories=hot_categories,
                           category_products=category_products)

@app.route('/search', methods=['GET', 'POST'])
def search():
    # 创建搜索表单实例
    search_form = SearchForm()

    # 当用户提交搜索表单时
    if search_form.validate_on_submit():
        # 获取用户输入的搜索词
        query = search_form.query.data

        # 在数据库中搜索商品名称包含搜索词的商品
        # ilike是不区分大小写的模糊搜索，%是通配符
        # 比如搜索"手机"，会匹配"华为手机"、"手机壳"等
        products = Product.query.filter(
            Product.name.ilike(f'%{query}%')
        ).all()

        # 渲染搜索结果页面
        return render_template('search_results.html',
                               products=products,
                               search_form=search_form)

    # 如果是直接访问搜索页面（GET请求）或表单验证失败
    # 重定向到首页
    return redirect(url_for('index'))