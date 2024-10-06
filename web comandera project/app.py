from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

# Crear la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta"

# Crear la base de datos si no existe
def crear_base_datos():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            total REAL NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Ruta principal para mostrar el formulario de pedidos
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para agregar un pedido
@app.route('/agregar_pedido', methods=['POST'])
def agregar_pedido():
    if request.method == 'POST':
        producto = request.form['producto']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        total = cantidad * precio

        # Guardar pedido en la base de datos
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pedidos (producto, cantidad, precio, total)
            VALUES (?, ?, ?, ?)
        ''', (producto, cantidad, precio, total))
        conn.commit()
        conn.close()
        
        flash("Pedido guardado con éxito.")
        return redirect(url_for('index'))

# Ruta para ver el reporte diario
@app.route('/reporte')
def reporte():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos")
    pedidos = cursor.fetchall()
    conn.close()

    total_ventas = sum([pedido[4] for pedido in pedidos])  # Sumando la columna de total
    return render_template('reporte.html', pedidos=pedidos, total_ventas=total_ventas)

# Ruta para editar un pedido
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Si es POST, actualizar los datos del pedido
    if request.method == 'POST':
        producto = request.form['producto']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        total = cantidad * precio

        cursor.execute('''
            UPDATE pedidos
            SET producto = ?, cantidad = ?, precio = ?, total = ?
            WHERE id = ?
        ''', (producto, cantidad, precio, total, id))
        conn.commit()
        conn.close()
        flash("Pedido actualizado con éxito.")
        return redirect(url_for('reporte'))
    
    # Si es GET, obtener los datos del pedido para mostrar en el formulario
    cursor.execute("SELECT * FROM pedidos WHERE id = ?", (id,))
    pedido = cursor.fetchone()
    conn.close()
    return render_template('editar.html', pedido=pedido)

# Ruta para eliminar un pedido
@app.route('/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pedidos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Pedido eliminado con éxito.")
    return redirect(url_for('reporte'))

# Crear base de datos y ejecutar la aplicación
if __name__ == '__main__':
    crear_base_datos()
    app.run(debug=True)
