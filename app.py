from flask import Flask,render_template,redirect,url_for,request,flash,session

from conexao import get_db_conection

import sqlite3

import base64

app = Flask(__name__)

app.secret_key = 'chavepararodar'




@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        usuario=request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        repetir_senha = request.form['repetir_senha']

        if senha == repetir_senha:
            conn = get_db_conection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
            usuario_existente = cursor.fetchone()

            if usuario_existente:
                flash('credencias ja existentes')
                conn.close()
                return render_template('site/cadastro.html')

            # Inserir o novo usuário
            cursor.execute('INSERT INTO usuarios (nome,email, senha) VALUES (?, ?, ?)', (usuario,email, senha))
            conn.commit()
            conn.close()
            flash('Cadastro realizado com sucesso')
            return redirect(url_for('login'))
        else:
            flash('As senhas têm que ser iguais')
            return render_template('site/cadastro.html')
    return render_template('site/cadastro.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = get_db_conection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        
        # Usar fetchone() para pegar apenas um usuário
        usuario = cursor.fetchone()
        
        conn.close()

        if usuario:
            # Verificar a senha aqui
            if senha == usuario['senha']:
                session['nome'] = usuario['nome']
                session['email'] = usuario['email']
                session['senha'] = usuario['senha']
                session['id'] = usuario['id']
                return redirect('/')
            else:
                error = 'Credenciais inválidas'
        else:
            error = 'Credenciais inválidas'
        
        return render_template('site/login_user.html', error=error)

    return render_template('site/login.html')





@app.route('/logout')
def logout():
    session.pop('nome', None)
    session.pop('email', None)
    session.pop('id', None)
    return redirect(url_for('login'))




@app.route("/",methods=['GET'])
def index():
    nome = session.get('nome')
    if 'nome' in session:
        nome = session.get('nome').split()[0]
    conn= get_db_conection()
    produtos= conn.execute('select p.id,p.img, p.imag, p.image, p.nome, p.descricao,p.preco, c.nome as nome_categoria from produtos p INNER join categorias c on p.id_categoria = c.id')
    categorias=conn.execute('SELECT * FROM categorias')
    slides= conn.execute('SELECT * FROM slides')
    return render_template('site/index.html', produtos=produtos,categorias=categorias,slides=slides,nome=nome)

@app.route("/site_listar_produto/<int:id>")
def site_listar_produto(id):

    nome = session.get('nome')
    if 'nome' in session:
        nome = session.get('nome').split()[0]


    conn= get_db_conection()
    produtos = conn.execute('select p.id,p.img, p.imag, p.image, p.nome, p.descricao,p.preco, c.nome as nome_categoria from produtos p INNER join categorias c on p.id_categoria = c.id WHERE c.id= ?', (id,)).fetchall()
    
    categorias=conn.execute('SELECT * FROM categorias').fetchall()
    

    #produtos = produtos if produtos is not None else []
    #categorias = categorias if categorias is not None else []

    conn.close()
    return render_template('site/listar_produto.html',produtos=produtos , categorias=categorias,nome=nome)

@app.route("/visualizar/<int:id>")
def visualizar(id):
    nome = session.get('nome')
    if 'nome' in session:
        nome = session.get('nome').split()[0]

    conn = get_db_conection()
    
    # Obter o produto (deve ser apenas um)
    produto = conn.execute('''SELECT p.*,c.nome AS nome_categoria FROM produtos p LEFT JOIN categorias c ON p.id_categoria = c.id WHERE p.id = ?''',                                                                                                                        (id,)).fetchone()
    # Consulta para obter os tamanhos do produto
    cursor = conn.execute('SELECT t.tamanho FROM produto_tamanhos pt INNER JOIN tamanhos t ON pt.tamanho_id=t.id WHERE pt.produto_id=?',(id,)).fetchall()
    
    # Obter todos os tamanhos do produto
    tamanhos = [tamanho['tamanho'] for tamanho in cursor]
    categorias=conn.execute('SELECT * FROM categorias').fetchall()
    
    return render_template("site/visualizar_tenis.html", produto=produto, tamanhos=tamanhos, nome=nome,categorias=categorias)
                                    #Rota admin

                    #pagina admin

@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email_adm')
        senha = request.form.get('senha_adm')

        conn = get_db_conection()
        cursor = conn.cursor()

        # Consulta parametrizada para evitar SQL Injection
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            # Verificação segura da senha usando hash (substitua por bibliotecas adequadas)
            if senha == usuario['senha']:
                session['nome'] = usuario['nome']
                session['email'] = usuario['email']
                session['ativo'] = usuario['ativo']
                session['id'] = usuario['id']
                return redirect('/admin')
            else:
                error = 'Credenciais inválidas'
        else:
            error = 'Credenciais inválidas'

    return render_template('admin/login.html', error=error)


@app.route("/admin")
def admin():
    conn = get_db_conection()
    produtos = conn.execute("SELECT count(id) FROM produtos").fetchone()[0]
    categorias= conn.execute("SELECT count(id) FROM categorias").fetchone()[0]
    return render_template('admin/index.html', categorias=categorias, produtos=produtos)

@app.route("/admin/listar_produto")
def listarProduto():

    conn = get_db_conection()
    produtos = conn.execute('''
        SELECT p.id, p.img, p.nome, p.descricao, p.preco, IFNULL(c.nome, 'sem categoria') AS nome_categoria FROM produtos p LEFT JOIN categorias c ON p.id_categoria = c.id''').fetchall()
    conn.close()
    return render_template('admin/listar-produto.html', produtos=produtos)


                                                                                                        #produtos

@app.route('/admin/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    conn=get_db_conection()
    categorias= conn.execute('SELECT * FROM categorias').fetchall()
    tamanho=conn.execute('SELECT * FROM tamanhos').fetchall()
    if request.method == 'POST':
        nome_produto = request.form.get('nome_produto')
        preco = request.form.get('preco')
        descricao = request.form.get('descricao')
        imagem = request.files.get('imagem')
        imagem1= request.files.get('imagem1')
        imagem2= request.files.get('imagem2')
        cat_id=request.form.get('id_categoria')
        tamanho_selecionado = request.form.getlist('tamanho')
        print(tamanho)
        

        existe_produto = conn.execute('SELECT * FROM produtos WHERE nome = ?', (nome_produto,)).fetchone()
        
        if existe_produto:
            flash('esse produto já existe')
            conn.close()
            return redirect(url_for('cadastrar_produto'))

        imagem_base64 = base64.b64encode(imagem.read()).decode('UTF-8')
        imagem_base32 = base64.b64encode(imagem1.read()).decode('UTF-8')
        imagem_base16 = base64.b64encode(imagem2.read()).decode('UTF-8')

        if nome_produto:
            conn = get_db_conection()
            con = conn.cursor()
            con.execute('INSERT INTO produtos (nome, descricao, preco, img, imag,image, id_categoria) VALUES (?, ?, ?, ?, ?, ?, ?)', 
            (nome_produto,  descricao, preco, imagem_base64, imagem_base32, imagem_base16, cat_id))
            produto_id = con.lastrowid

            for tamanho_id in tamanho_selecionado:
                con.execute("INSERT INTO produto_tamanhos (produto_id, tamanho_id) VALUES (?, ?)", (produto_id, tamanho_id))

            conn.commit()
            conn.close()
            flash(f'produto {nome_produto} cadastrado com sucesso')
            return redirect(url_for('admin'))        
    return render_template('admin/cadastrar_produto.html', categorias=categorias,tamanhos=tamanho)

@app.route("/admin/editar_produto/<int:id>", methods=['GET', 'POST'])
def editarProduto(id):
    conn = get_db_conection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    categorias = conn.execute('SELECT * FROM categorias').fetchall()
    todos_os_tamanhos = conn.execute('SELECT * FROM tamanhos').fetchall()
    
    # tamanhos do produto
    tamanhos_associados = conn.execute('''SELECT t.id, t.tamanho FROM tamanhos t JOIN produto_tamanhos pt ON t.id = pt.tamanho_id WHERE pt.produto_id = ?''',(id,)).fetchall()

    tamanhos_associados_ids = [tamanho['id'] for tamanho in tamanhos_associados]

    if request.method == 'POST':
        nome_produto = request.form.get('nome_produto')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        imagem = request.files.get('imagem')
        imagem1 = request.files.get('imagem1')
        imagem2 = request.files.get('imagem2')
        id_categoria = request.form.get('id_categoria')
        tamanho_selecionado = request.form.getlist('tamanho')

        imagem_base64 = base64.b64encode(imagem.read()).decode('UTF-8')
        imagem_base32 = base64.b64encode(imagem1.read()).decode('UTF-8')
        imagem_base16 = base64.b64encode(imagem2.read()).decode('UTF-8')

        if imagem and imagem2:
            # Atualizar os dados do produto
            conn.execute('UPDATE produtos SET nome=?, descricao=?, preco=?, img=?, imag=?, image=?, id_categoria=? WHERE id=?',
                         (nome_produto, descricao, preco, imagem_base64, imagem_base32, imagem_base16, id_categoria, id))
            conn.execute('DELETE FROM produto_tamanhos WHERE produto_id = ?', (id,))
            
            for tamanho_id in tamanho_selecionado:
                conn.execute('INSERT INTO produto_tamanhos (produto_id, tamanho_id) VALUES (?, ?)', (id, tamanho_id))
        
            conn.commit()
            conn.close()
            
            flash(f'Produto {nome_produto} editado com sucesso')
            return redirect(url_for('admin'))
        else:

            # Atualizar os dados do produto
            conn.execute('UPDATE produtos SET nome=?, descricao=?, preco=?,  id_categoria=? WHERE id=?',
                         (nome_produto, descricao, preco, id_categoria, id))
            conn.execute('DELETE FROM produto_tamanhos WHERE produto_id = ?', (id,))
            
            for tamanho_id in tamanho_selecionado:
                conn.execute('INSERT INTO produto_tamanhos (produto_id, tamanho_id) VALUES (?, ?)', (id, tamanho_id))
        
            conn.commit()
            conn.close()

            flash(f'Produto {nome_produto} editado com sucesso')
            return redirect(url_for('admin'))

    conn.close()
    
    return render_template('admin/editar_produto.html', produto=produto, categorias=categorias, todos_os_tamanhos=todos_os_tamanhos, tamanhos_associados_ids=tamanhos_associados_ids)


@app.route("/admin/excluir_produto/<int:id>", methods=['GET', 'POST'])
def excluirProduto(id):
    conn= get_db_conection()
    produtos= conn.execute('SELECT * FROM  produtos WHERE id = ?', (id,)).fetchone()
    nome_produto=produtos['nome']
    if request.method == 'POST':
        conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
        conn.execute("DELETE FROM produto_tamanhos WHERE produto_id = ?", (id,))
        conn.execute("DELETE FROM  produto_tamanhos WHERE produto_id= ?", (id,))
        conn.commit()
        conn.close()
        flash(f'produto {nome_produto} excluido com sucesso')
        return redirect(url_for('admin'))
    conn.close()

    return render_template('admin/excluir_produto.html',produtos=produtos)


# excluir id produto
@app.route("/admin/excluir_por_idProduto", methods=['GET','POST'])
def ExcluirIDproduto():
    conn= get_db_conection()
    produto=conn.execute('select * from produtos').fetchone()

    if request.method =='POST':
        produtos=produto['nome']
        id = request.form.get('id')

        existe_produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
        
        if not existe_produto:
            flash('esse produto não existe')
            conn.close()
            return redirect(url_for('ExcluirIDproduto'))


        conn.execute(f'DELETE FROM produtos WHERE id = {id}')
        conn.commit()
        conn.close()
        flash(f'produtos {produtos}  excluido com sucesso')
        return redirect(url_for('admin'))
    return render_template('admin/ID_excluiproduto.html',produto=produto)


                                                                                                                #categorias


#inicio das rotas de categoria
@app.route("/admin/listar")
def listarCategoria():
    conn = get_db_conection()
    categorias = conn.execute('SELECT * FROM categorias').fetchall()

    conn.close()
    return render_template('admin/listar-categoria.html', categorias=categorias)

@app.route("/admin/cadastrar_categoria", methods=['GET', 'POST'])
def cadastrar_categoria():
    if request.method == 'POST':
        nome_categoria = request.form.get('nome_categoria')
        descricao = request.form.get('descricao')
        conn = get_db_conection()
        existe_categoria = conn.execute('SELECT * FROM categorias WHERE nome = ?', (nome_categoria,)).fetchone()
        
        if existe_categoria:
            flash('Já existe uma categoria com esse nome')
            conn.close()
            return redirect(url_for('cadastrar_categoria'))

        if nome_categoria:
            conn = get_db_conection()
            conn.execute('INSERT INTO categorias (nome, descricao ) VALUES (?, ?)',
                (nome_categoria, descricao))
            
            conn.commit()
            conn.close()
            flash(f'Categoria {nome_categoria} cadastrada com sucesso')
            return redirect(url_for('admin'))        
    return render_template('admin/cadastrar_categoria.html')



# Rota para excluir categoria
@app.route("/admin/excluir_categoria/<int:id>", methods=['GET', 'POST'])
def excluirCategoria(id):
    conn = get_db_conection()
    categorias = conn.execute('SELECT * FROM categorias WHERE id = ?', (id,)).fetchone()
    nome_categoria= categorias['nome']
    if request.method == 'POST':
        conn.execute('DELETE FROM categorias WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash(f'Categoria {nome_categoria} excluida com sucesso')
        return redirect(url_for('admin'))
    
    conn.close()
    return render_template('admin/excluir_categoria.html', categorias=categorias)


@app.route("/admin/editar_categoria/<int:id>", methods=['GET', 'POST'])
def editarCategoria(id):
    conn = get_db_conection()
    categoria = conn.execute('SELECT * FROM categorias WHERE id = ?', (id,)).fetchone()    
    
    if request.method == 'POST':
        nome_categoria = request.form.get('nome_categoria')
        descricao = request.form.get('descricao')

        if nome_categoria:
            conn.execute('UPDATE categorias SET nome=?, descricao=? WHERE id=?', 
                         (nome_categoria, descricao, id,))
            conn.commit()
            conn.close()
            flash(f'Categoria {nome_categoria} editada com sucesso')
            return redirect(url_for('admin')) 
    return render_template('admin/editar_categoria.html', categoria=categoria)


                                                                                                                        # excluir id categoria
@app.route("/admin/excluir_por_idcategoria", methods=['GET','POST'])
def ExcluirIDcategoria():
    conn= get_db_conection()
    categoria=conn.execute('select * from categorias').fetchone()
    
    if request.method =='POST':
        categorias=categoria['nome']
        id = request.form.get('id')


        existe_categorias = conn.execute('SELECT * FROM categorias WHERE id = ?', (id,)).fetchone()
        if not existe_categorias:
            flash('essa categoria não existe')
            conn.close()
            return redirect(url_for('ExcluirIDcategoria'))


        conn.execute(f'DELETE FROM categorias WHERE id = {id}')
        conn.commit()
        conn.close()
        flash(f'categoria {categorias}  excluido com sucesso')
        return redirect(url_for('admin'))
    return render_template('admin/ID_excluicategoria.html',categoria=categoria)

                                                                                                            #Rotas slides


@app.route('/admin/cadastro_slides', methods=['GET', 'POST'])
def cadastro_slides():
    if request.method == "POST":
        slide =request.files.get('slide')
        print(slide)
        if slide:
            imagem_base64 = base64.b64encode(slide.read()).decode('UTF-8')
            conn = get_db_conection()
            conn.execute('INSERT INTO slides (slide) VALUES (?)', 
            ( imagem_base64,))
            conn.commit()
            conn.close()
            flash(f'imagem cadastrado com sucesso')
            return redirect(url_for('admin'))
    return render_template('admin/cadastro_slides.html')




@app.route("/admin/listar-slide")
def listarSlide():
    conn = get_db_conection()
    slides = conn.execute('SELECT * FROM slides').fetchall()

    conn.close()
    return render_template('admin/listar-slide.html', slides=slides)


@app.route("/admin/excluir_por_IDslide", methods=['GET','POST'])
def ExcluirIDslide():
    conn= get_db_conection()
    slides = conn.execute('SELECT * FROM slides').fetchall()
    if request.method =='POST':
        id = request.form.get('id')

        existe_slide = conn.execute('SELECT * FROM slides WHERE id = ?', (id,)).fetchone()
        
        if not existe_slide:
            flash('esse slide não existe')
            conn.close()
            return redirect(url_for('ExcluirIDslide'))


        conn.execute(f'DELETE FROM slides WHERE id = {id}')
        conn.commit()
        conn.close()

        flash(f'slide id {id} excluido com sucesso')
        return redirect(url_for('admin'))

    return render_template('admin/ID_excluislide.html',slides=slides)



# Rota para excluir categoria
@app.route("/admin/excluir_slide/<int:id>", methods=['GET', 'POST'])
def excluirSlide(id):
    conn = get_db_conection()
    slides = conn.execute('SELECT * FROM slides WHERE id = ?', (id,)).fetchone()
    nome_slide= slides['id']
    if request.method == 'POST':
        conn.execute('DELETE FROM slides WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash(f'slide {nome_slide} excluida com sucesso')
        return redirect(url_for('admin'))
    
    conn.close()
    return render_template('admin/excluir_slide.html', slides=slides)

@app.route("/admin/editar_slide/<int:id>", methods=['GET', 'POST'])
def editarSlide(id):
    conn = get_db_conection()
    slides = conn.execute('SELECT * FROM slides WHERE id = ?', (id,)).fetchone()    
    
    if request.method == 'POST':
        slide = request.files.get('slide')
        slide_base64 = base64.b64encode(slide.read()).decode('UTF-8')

        if slide_base64:
            conn.execute('UPDATE slides SET slide=? WHERE id=?', 
                         (slide_base64,id,))
            conn.commit()
            conn.close()
            flash(f'slide editado com sucesso')
            return redirect(url_for('admin')) 
    return render_template('admin/editar_slide.html', slides=slides)


# status do banco de dados botão pro admin
@app.route('/ligar_slide/<int:id>')
def ligar_slide(id):
    conn = get_db_conection()
    
    # Atualiza o status da denuncia para 'on'
    conn.execute('UPDATE slides SET status = ? WHERE id = ?', ('on', id))
    conn.commit()

    return redirect(url_for('listarSlide'))


@app.route('/desligar_slide/<int:id>')
def desligar_slide(id):
    conn = get_db_conection()
    
    # atualizar o status da denuncia para 'off'
    conn.execute('UPDATE slides SET status = ? WHERE id = ?', ('off', id))
    conn.commit()

    return redirect(url_for('listarSlide'))


                                                                                             # rota para de tamanhos dos tenis

@app.route('/admin/cadastrar_tamanho', methods=['GET', 'POST'])
def cadastrar_tamanho():
    conn=get_db_conection()
    if request.method == 'POST':
        tamanhos = request.form.get('tamanho_tenis')

        if tamanhos:
            conn = get_db_conection()

            existe_tamanho = conn.execute('SELECT * FROM tamanhos WHERE tamanho = ?', (tamanhos,)).fetchone()
            
            if existe_tamanho:
                flash('Já existe uma categoria com esse tamanho')
                conn.close()
                return redirect(url_for('cadastrar_tamanho'))

            conn.execute('INSERT INTO tamanhos (tamanho) VALUES (?)', (tamanhos,))

            conn.commit()
            conn.close()
            flash(f'tamanho {tamanhos} cadastrado com sucesso')
            return redirect(url_for('admin'))
    return render_template('admin/cadastrar_tamanho.html')

@app.route("/admin/listar-tamanho")
def listarTamanho():
    conn = get_db_conection()
    tamanhos = conn.execute('SELECT * FROM tamanhos').fetchall()

    conn.close()
    return render_template('admin/listar-tamanho.html', tamanhos=tamanhos)


@app.route("/admin/editar_tamanho/<int:id>", methods=['GET', 'POST'])
def editarTamanho(id):
    conn = get_db_conection()
    tamanhos = conn.execute('SELECT * FROM tamanhos WHERE id = ?', (id,)).fetchone()    
    
    if request.method == 'POST':
        tamanho = request.form.get('tamanho')

        if tamanho:
            conn.execute('UPDATE tamanhos SET tamanho=? WHERE id=?', (tamanho,id,))
            conn.commit()
            conn.close()
            flash(f' novo tamanho {tamanho} editada com sucesso')
            return redirect(url_for('admin')) 
    return render_template('admin/editar_tamanho.html', tamanhos=tamanhos)

@app.route("/admin/excluir_tamanho/<int:id>", methods=['GET', 'POST'])
def excluirTamanho(id):
    conn = get_db_conection()
    tamanhos = conn.execute('SELECT * FROM tamanhos WHERE id = ?', (id,)).fetchone()
    nome_tamanho= tamanhos['tamanho']
    if request.method == 'POST':
        conn.execute('DELETE FROM tamanhos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash(f'tamanho {nome_tamanho} excluida com sucesso')
        return redirect(url_for('admin'))
    
    conn.close()
    return render_template('admin/excluir_tamanho.html', tamanhos=tamanhos)

@app.route("/admin/excluir_por_IDtamanho", methods=['GET','POST'])
def ExcluirIDtamanho():
    conn= get_db_conection()
    tamanhos = conn.execute('SELECT * FROM tamanhos').fetchall()
    if request.method =='POST':
        id = request.form.get('id')
        print(id)
        
        existe_tamanhos = conn.execute('SELECT * FROM tamanhos WHERE id = ?', (id,)).fetchone()
        if not existe_tamanhos:
            flash('esse tamanho não existe')
            conn.close()
            return redirect(url_for('ExcluirIDtamanho'))

        tamanho_nome=conn.execute(f'SELECT * FROM tamanhos WHERE id = {id}').fetchone()
        nome=tamanho_nome['tamanho']

        conn.execute(f'DELETE FROM tamanhos WHERE id = {id}')
        conn.commit()
        conn.close()
        flash(f'tamanho {nome} excluido com sucesso')
        return redirect(url_for('admin'))
    return render_template('admin/ID_exclui_tamanho.html',tamanhos=tamanhos)



app.run(debug=True)