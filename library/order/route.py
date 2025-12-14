import os
from flask import Blueprint, render_template, request, session, redirect, url_for
from order.model_route import model_route, model_route_add, model_route_insert,model_route_client
from database.sql_provider import SQLProvider
from access import group_required

blueprint_order = Blueprint(
    'blueprint_order',
    __name__,
    template_folder='templates'
)

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@blueprint_order.route('/client', methods=["GET","POST"])
@group_required
def client():
    if request.method == "POST":
        user_input = request.form
        session['surname'] = user_input['surname']
        session['name'] = user_input['name']
        result_info = model_route_client(provider, user_input, 'client.sql', 'select')
        if result_info.status:
            results = result_info.result
            session['Cl_id'] = results[0]['Cl_id']
            return render_template('client_found.html',surname=user_input['surname'],name=user_input['name'])
        else:
            return render_template('client_notfound.html',surname=user_input['surname'],name=user_input['name'])
    else:
        return render_template("client.html")

@blueprint_order.route('/client_add', methods=["POST"])
@group_required
def client_add():
    user_input = {'surname': session['surname'], 'name': session['name']}
    session['Cl_id'] = model_route_client(provider, user_input, 'insert_client.sql', 'insert').result
    if session['Cl_id']:
        return render_template('client_found.html',surname=user_input['surname'],name=user_input['name'])
    else:
        return render_template("basket_err.html",error="добавлении нового пользователя")

@blueprint_order.route('/', methods=["GET"])
@group_required
def order_index():
    if 'Cl_id' not in session:
        return redirect(url_for('blueprint_order.client'))
    user_input={}
    result_info = model_route(provider, user_input , 'books.sql')
    items = result_info.result
    basket=session.get('basket')
    for item in items:
        item['amount'] = item['book_number']
        if basket:
            for key in basket:
                if int(key) == item['book_id']:
                    item['amount'] = 0
                    break
    return render_template("basket_order_list.html", items=items, basket=basket)

@blueprint_order.route('/add', methods=["POST"])
@group_required
def add_index():
    user_input=request.form
    result_status = model_route_add(provider, user_input, 'book.sql')
    if result_status:
        return redirect(url_for('blueprint_order.order_index'))
    else:
        return render_template("basket_err.html",error="добавлении книги в заказ")

@blueprint_order.route('/clear', methods=["GET"])
@group_required
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect(url_for('blueprint_order.order_index'))

@blueprint_order.route('/save', methods=["GET"])
@group_required
def save_order():
    if 'basket' in session:
        o_id = model_route_insert(provider, 'insert_o.sql', 'insert_ol.sql','books.sql')
        if o_id:
            session.pop('basket')
            return render_template("order_saved.html",o_id=o_id)
        else:
            return render_template("basket_err.html",error="формировании заказа")
    else:
        return redirect(url_for('blueprint_order.order_index'))

@blueprint_order.route('/exit', methods=["GET"])
@group_required
def exit():
    if 'Cl_id' in session:
        session.pop('Cl_id')
    if 'name' in session:
        session.pop('surname')
        session.pop('name')
    if 'basket' in session:
        session.pop('basket')
    return redirect('/')