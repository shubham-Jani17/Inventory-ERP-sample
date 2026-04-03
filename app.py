from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from config import DB_CONFIG, SECRET_KEY
from datetime import date

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ─────────────────────────────────────────────
# DB HELPER
# ─────────────────────────────────────────────

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=(), fetch='all'):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    if fetch == 'all':
        result = cur.fetchall()
    elif fetch == 'one':
        result = cur.fetchone()
    else:
        conn.commit()
        result = cur.lastrowid
    cur.close()
    conn.close()
    return result


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@app.route('/')
def dashboard():
    total_items   = query("SELECT COUNT(*) as c FROM items", fetch='one')['c']
    total_stock   = query("SELECT SUM(quantity) as s FROM items", fetch='one')['s'] or 0
    low_stock     = query("SELECT COUNT(*) as c FROM items WHERE quantity <= reorder_level", fetch='one')['c']
    total_value   = query("SELECT SUM(quantity * rate) as v FROM items", fetch='one')['v'] or 0

    recent_txns = query("""
        SELECT t.*, i.item_name, i.item_code
        FROM transactions t
        JOIN items i ON t.item_id = i.id
        ORDER BY t.created_at DESC LIMIT 8
    """)

    low_stock_items = query("""
        SELECT * FROM items WHERE quantity <= reorder_level ORDER BY quantity ASC LIMIT 5
    """)

    # Category-wise stock for chart
    category_data = query("""
        SELECT category, SUM(quantity) as total FROM items GROUP BY category
    """)

    return render_template('dashboard.html',
        total_items=total_items,
        total_stock=int(total_stock),
        low_stock=low_stock,
        total_value=total_value,
        recent_txns=recent_txns,
        low_stock_items=low_stock_items,
        category_data=category_data
    )


# ─────────────────────────────────────────────
# ITEMS
# ─────────────────────────────────────────────

@app.route('/items')
def items():
    search = request.args.get('search', '')
    category = request.args.get('category', '')

    sql = "SELECT * FROM items WHERE 1=1"
    params = []
    if search:
        sql += " AND (item_name LIKE %s OR item_code LIKE %s)"
        params += [f'%{search}%', f'%{search}%']
    if category:
        sql += " AND category = %s"
        params.append(category)
    sql += " ORDER BY created_at DESC"

    all_items = query(sql, params)
    categories = query("SELECT DISTINCT category FROM items ORDER BY category")

    return render_template('items.html', items=all_items, categories=categories,
                           search=search, selected_category=category)


@app.route('/items/add', methods=['POST'])
def add_item():
    code  = request.form['item_code'].strip().upper()
    name  = request.form['item_name'].strip()
    cat   = request.form['category'].strip()
    qty   = int(request.form['quantity'] or 0)
    unit  = request.form['unit'].strip()
    rl    = int(request.form['reorder_level'] or 10)
    rate  = float(request.form['rate'] or 0)

    try:
        query("""
            INSERT INTO items (item_code, item_name, category, quantity, unit, reorder_level, rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (code, name, cat, qty, unit, rl, rate), fetch='commit')
        flash(f'Item "{name}" added successfully!', 'success')
    except mysql.connector.IntegrityError:
        flash(f'Item code "{code}" already exists.', 'error')

    return redirect(url_for('items'))


@app.route('/items/edit/<int:item_id>', methods=['POST'])
def edit_item(item_id):
    name  = request.form['item_name'].strip()
    cat   = request.form['category'].strip()
    unit  = request.form['unit'].strip()
    rl    = int(request.form['reorder_level'] or 10)
    rate  = float(request.form['rate'] or 0)

    query("""
        UPDATE items SET item_name=%s, category=%s, unit=%s, reorder_level=%s, rate=%s
        WHERE id=%s
    """, (name, cat, unit, rl, rate, item_id), fetch='commit')
    flash('Item updated successfully!', 'success')
    return redirect(url_for('items'))


@app.route('/items/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = query("SELECT item_name FROM items WHERE id=%s", (item_id,), fetch='one')
    query("DELETE FROM transactions WHERE item_id=%s", (item_id,), fetch='commit')
    query("DELETE FROM items WHERE id=%s", (item_id,), fetch='commit')
    flash(f'Item "{item["item_name"]}" deleted.', 'info')
    return redirect(url_for('items'))


@app.route('/api/item/<int:item_id>')
def get_item(item_id):
    item = query("SELECT * FROM items WHERE id=%s", (item_id,), fetch='one')
    return jsonify(item)


# ─────────────────────────────────────────────
# TRANSACTIONS
# ─────────────────────────────────────────────

@app.route('/transactions')
def transactions():
    txn_type = request.args.get('type', '')
    item_filter = request.args.get('item_id', '')

    sql = """
        SELECT t.*, i.item_name, i.item_code, i.unit
        FROM transactions t
        JOIN items i ON t.item_id = i.id
        WHERE 1=1
    """
    params = []
    if txn_type:
        sql += " AND t.transaction_type = %s"
        params.append(txn_type)
    if item_filter:
        sql += " AND t.item_id = %s"
        params.append(item_filter)
    sql += " ORDER BY t.created_at DESC"

    all_txns = query(sql, params)
    all_items = query("SELECT id, item_code, item_name FROM items ORDER BY item_name")

    return render_template('transactions.html',
                           transactions=all_txns, items=all_items,
                           selected_type=txn_type, selected_item=item_filter)


@app.route('/transactions/add', methods=['POST'])
def add_transaction():
    item_id  = int(request.form['item_id'])
    txn_type = request.form['transaction_type']
    qty      = int(request.form['quantity'])
    note     = request.form.get('note', '').strip()
    txn_date = request.form.get('date') or str(date.today())

    # Check stock for OUT transactions
    item = query("SELECT * FROM items WHERE id=%s", (item_id,), fetch='one')
    if txn_type == 'OUT' and item['quantity'] < qty:
        flash(f'Insufficient stock! Available: {item["quantity"]} {item["unit"]}', 'error')
        return redirect(url_for('transactions'))

    query("""
        INSERT INTO transactions (item_id, transaction_type, quantity, note, date)
        VALUES (%s, %s, %s, %s, %s)
    """, (item_id, txn_type, qty, note, txn_date), fetch='commit')

    # Update item quantity
    if txn_type == 'IN':
        query("UPDATE items SET quantity = quantity + %s WHERE id=%s", (qty, item_id), fetch='commit')
    else:
        query("UPDATE items SET quantity = quantity - %s WHERE id=%s", (qty, item_id), fetch='commit')

    action = 'added to' if txn_type == 'IN' else 'removed from'
    flash(f'{qty} units {action} stock for "{item["item_name"]}"!', 'success')
    return redirect(url_for('transactions'))


# ─────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
