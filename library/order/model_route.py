from dataclasses import dataclass
from database.select import select_dict, insert_many,insert
from flask import session, current_app
from cache.wrapper import fetch_from_cache

@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str

def model_route_client(provider, user_input: dict, sql_file: str,action:str):
    err_message = ""
    _sql = provider.get(sql_file)
    if action == "insert":
        result = insert(_sql, dict(user_input))
    else:
        result = select_dict(_sql, user_input)
    if result:
        return ResultInfo(result=result, status=True, err_message=err_message)
    else:
        return ResultInfo(result=result, status=False, err_message="DATA NOT FOUND")

def model_route(provider, user_input: dict, sql_file: str):
    cache_config = current_app.config['cache_config']
    cache_select = fetch_from_cache('some_items_cached', cache_config)(select_dict)
    err_message = ""
    _sql = provider.get(sql_file)
    result = cache_select(_sql, user_input)
    if result:
        return ResultInfo(result=result, status=True, err_message=err_message)
    else:
        return ResultInfo(result=result, status=False, err_message="DATA NOT FOUND")

def model_route_add(provider, user_input: dict, sql_file: str):
    _sql = provider.get(sql_file)
    substr=False
    if user_input['action'] == 'Удалить':
        substr = True
    user_dict = {'book_id': user_input['book_id']}
    result = select_dict(_sql, user_dict)
    if result:
        add_to_basket(result[0],substr)
        return True
    else:
        return False

def add_to_basket(books: dict,substr: bool):
    if 'basket' not in session:
        session['basket'] = {}
    book_id = str(books['book_id'])
    if substr:
        session['basket'].pop(book_id)
        return True
    else:
        session['basket'][book_id] = {'book_name': books['book_name'],'book_author': books['book_author'], 'book_number': 1}
    return True

def model_route_insert(provider, sql_file1: str, sql_file2: str, sql_check: str):
    if check_basket(provider,sql_check):
        return False
    _sql1 = provider.get(sql_file1)
    _sql2 = provider.get(sql_file2)
    result = insert_many(_sql1, _sql2)
    if result:
        bill_id = result
        return bill_id
    return False

def check_basket(provider, sql_file: str):
    _sql = provider.get(sql_file)
    result = select_dict(_sql, {})
    basket = session.get('basket')
    for item in result:
        for key in basket:
            if int(key) == item['book_id'] and basket[key]['book_number'] > item['book_number']:
                return True
    return False
